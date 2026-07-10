import json
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request

import sys
sys.path.append(str(Path(__file__).resolve().parents[3]))
from telegram_notifier import send_telegram_notification
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent.parent

app = Flask(
    __name__,
    static_folder=str(PROJECT_ROOT),
    static_url_path="/static",
    template_folder=str(PROJECT_ROOT / "frontend-html" / "chat"),
)
app.config['SECRET_KEY'] = 'secret_key_123'
socketio = SocketIO(app, cors_allowed_origins="*")

# Файлове сховище для логів (у реальному проекті тут буде база даних)
DATA_DIR = PROJECT_ROOT / "resources-database" / "chat"
HISTORY_FILE = DATA_DIR / "chat_history.json"
UPLOAD_DIR = PROJECT_ROOT / "resources" / "chat" / "uploads"
STICKER_DIR = PROJECT_ROOT / "resources" / "resources-assets" / "stick"
chat_history = {}
admin_to_user = {}
user_to_admin = {}


def get_sticker_catalog():
    stickers = []
    if not STICKER_DIR.exists():
        return stickers

    for path in sorted(STICKER_DIR.glob("*.png")):
        sticker_id = path.stem
        stickers.append(
            {
                "id": sticker_id,
                "name": sticker_id.replace("_", " "),
                "url": f"/static/resources/resources-assets/stick/{path.name}",
            }
        )
    return stickers


STICKERS = get_sticker_catalog()
STICKER_URLS = {item["url"] for item in STICKERS}

def load_store():
    if not HISTORY_FILE.exists():
        return {"history": {}, "admin_to_user": {}, "user_to_admin": {}}
    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return {"history": {}, "admin_to_user": {}, "user_to_admin": {}}

    # Міграція зі старого формату: {log_id: [messages]}
    if data and all(isinstance(v, list) for v in data.values()):
        return {"history": data, "admin_to_user": {}, "user_to_admin": {}}

    return {
        "history": data.get("history", {}),
        "admin_to_user": data.get("admin_to_user", {}),
        "user_to_admin": data.get("user_to_admin", {}),
    }

def save_store():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "history": chat_history,
                "admin_to_user": admin_to_user,
                "user_to_admin": user_to_admin,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

store = load_store()
chat_history = store["history"]
admin_to_user = store["admin_to_user"]
user_to_admin = store["user_to_admin"]


def normalize_files(items):
    normalized = []
    for item in items or []:
        if not isinstance(item, dict):
            continue

        url = str(item.get("url") or "").strip()
        name = str(item.get("name") or "file").strip() or "file"
        mime_type = str(item.get("type") or "application/octet-stream").strip() or "application/octet-stream"

        if not url.startswith("/static/resources/chat/uploads/"):
            continue

        normalized.append(
            {
                "url": url,
                "name": name,
                "type": mime_type,
                "size": int(item.get("size") or 0),
                "is_image": bool(item.get("is_image")),
            }
        )
    return normalized

def resolve_room(log_id):
    return admin_to_user.get(log_id, log_id)

def create_logs():
    user_log_id = str(uuid.uuid4())[:8]
    admin_log_id = str(uuid.uuid4())[:8]
    while user_log_id in chat_history or user_log_id in admin_to_user or user_log_id in user_to_admin:
        user_log_id = str(uuid.uuid4())[:8]
    while admin_log_id in chat_history or admin_log_id in admin_to_user or admin_log_id in user_to_admin:
        admin_log_id = str(uuid.uuid4())[:8]

    chat_history.setdefault(user_log_id, [])
    admin_to_user[admin_log_id] = user_log_id
    user_to_admin[user_log_id] = admin_log_id
    save_store()
    return user_log_id, admin_log_id

@app.route('/')
def index():
    # Генеруємо новий унікальний "лог" (UUID) для нового відвідувача
    user_log_id, _admin_log_id = create_logs()
    return render_template('index.html', log_id=user_log_id, role='user', stickers=STICKERS)

@app.route('/log/<log_id>')
def user_chat(log_id):
    # Вхід користувача у свій існуючий лог
    if log_id not in chat_history:
        # Створюємо дзеркальний лог для адміна, якщо користувача ще не було
        chat_history.setdefault(log_id, [])
        admin_log_id = str(uuid.uuid4())[:8]
        while admin_log_id in chat_history or admin_log_id in admin_to_user or admin_log_id in user_to_admin:
            admin_log_id = str(uuid.uuid4())[:8]
        admin_to_user[admin_log_id] = log_id
        user_to_admin[log_id] = admin_log_id
        save_store()
    return render_template('index.html', log_id=log_id, role='user', stickers=STICKERS)

@app.route('/admin')
def admin_logs():
    # Список всіх наявних логів
    pairs = sorted(
        [(user, user_to_admin.get(user, "")) for user in chat_history.keys()],
        key=lambda x: x[0],
    )
    return render_template('admin_list.html', pairs=pairs)

@app.route('/admin/<log_id>')
def admin_chat(log_id):
    # Вхід для вас як адміна по конкретному логу
    user_log_id = resolve_room(log_id)
    if user_log_id not in chat_history:
        chat_history.setdefault(user_log_id, [])
        save_store()
    return render_template('index.html', log_id=user_log_id, role='admin', stickers=STICKERS)


@app.route('/upload', methods=['POST'])
def upload_files():
    room = resolve_room((request.form.get('room') or '').strip())
    if not room:
        return jsonify({'ok': False, 'error': 'missing_room'}), 400

    uploaded = request.files.getlist('files')
    if not uploaded:
        return jsonify({'ok': False, 'error': 'missing_files'}), 400

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    files = []

    for storage in uploaded:
        original_name = secure_filename(storage.filename or 'file')
        if not original_name:
            original_name = 'file'

        ext = Path(original_name).suffix
        stored_name = f"{uuid.uuid4().hex}{ext}"
        dest = UPLOAD_DIR / stored_name
        storage.save(dest)

        mime_type = storage.mimetype or 'application/octet-stream'
        files.append(
            {
                'name': original_name,
                'url': f'/static/resources/chat/uploads/{stored_name}',
                'type': mime_type,
                'size': dest.stat().st_size,
                'is_image': mime_type.startswith('image/'),
            }
        )

    return jsonify({'ok': True, 'files': files})

@socketio.on('join')
def on_join(data):
    room = resolve_room(data['room'])
    join_room(room)
    # Відправляємо історію, якщо вона є
    if room in chat_history:
        emit('history', chat_history[room])

@socketio.on('send_message')
def handle_message(data):
    room = resolve_room(data['room'])
    text = str(data.get('text') or '').strip()
    files = normalize_files(data.get('files') or [])
    sticker = str(data.get('sticker') or '').strip()
    if sticker and sticker not in STICKER_URLS:
        sticker = ''

    if not text and not files and not sticker:
        return

    msg = {
        'text': text,
        'sender': data['role'],
        'time': data['time'],
        'files': files,
        'sticker': sticker,
    }
    
    if room not in chat_history:
        chat_history[room] = []
    chat_history[room].append(msg)
    save_store()
    
    # Розсилаємо повідомлення всім у цій кімнаті (вам і користувачу)
    emit('receive_message', msg, room=room)

    sender_role = 'адмін' if data.get('role') == 'admin' else 'користувач'
    sender_name = data.get('name') or sender_role
    message_text = text or (f"[Файл: {', '.join(file['name'] for file in files)}]" if files else "[стікер]")
    notification_text = (
        f"📨 Нове повідомлення в чаті\n"
        f"Кімната: {room}\n"
        f"Від: {sender_name}\n"
        f"Текст: {message_text}"
    )
    send_telegram_notification(notification_text)

if __name__ == '__main__':
    import os
    port = int(os.getenv("PORT", "5001"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, use_reloader=False)
