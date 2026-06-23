from flask import Flask, request, jsonify, send_from_directory
from email.message import EmailMessage
from pathlib import Path
import json
import smtplib
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
ENTRY_TEMPLATE_DIR = PROJECT_ROOT / 'frontend-html' / 'entry'
ENTRY_DATA_DIR = PROJECT_ROOT / 'resources-database' / 'entry'

app = Flask(__name__, static_folder=None)


def load_json(path, default):
    if not path.exists():
        return default
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default


def save_json(path, data):
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def send_email(subject, body, config):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config['from_email']
    msg['To'] = config['to_email']
    msg.set_content(body)

    host = config['smtp_host']
    port = int(config.get('smtp_port', 587))
    user = config['smtp_user']
    password = config['smtp_password']
    use_tls = bool(config.get('use_tls', True))

    if use_tls:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(user, password)
            server.send_message(msg)


@app.route('/')
def index():
    return send_from_directory(ENTRY_TEMPLATE_DIR, 'index.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    key = (data.get('key') or '').strip()
    students = load_json(ENTRY_DATA_DIR / 'students.json', {})
    student = students.get(key)
    if not student:
        return jsonify({'ok': False})
    name = student.get('name') or 'Учень'
    return jsonify({'ok': True, 'name': name})


@app.route('/api/apply', methods=['POST'])
def api_apply():
    data = request.get_json(silent=True) or {}
    required = ['studentName', 'phone']
    if any(not (data.get(k) or '').strip() for k in required):
        return jsonify({'ok': False, 'error': 'missing_fields'})

    payload = {
        'subject': data.get('subject', 'Не вказано'),
        'teacher': data.get('teacher', 'Не вказано'),
        'studentName': data.get('studentName', 'Не вказано'),
        'studentClass': data.get('studentClass', 'Не вказано'),
        'phone': data.get('phone', 'Не вказано'),
        'message': data.get('message', '—'),
        'createdAt': datetime.now(timezone.utc).isoformat()
    }

    config = load_json(ENTRY_DATA_DIR / 'config.json', {})
    if not config:
        return jsonify({'ok': False, 'error': 'missing_config'})

    email_body = (
        'Нова заявка (MrBlackFox)\n\n'
        f"Предмет: {payload['subject']}\n"
        f"Викладач: {payload['teacher']}\n"
        f"Учень: {payload['studentName']}\n"
        f"Клас: {payload['studentClass']}\n"
        f"Телефон: {payload['phone']}\n"
        f"Повідомлення: {payload['message']}\n"
        f"Час (UTC): {payload['createdAt']}\n"
    )

    try:
        send_email('Нова заявка MrBlackFox', email_body, config)
    except Exception:
        return jsonify({'ok': False, 'error': 'email_failed'})

    applications_path = ENTRY_DATA_DIR / 'applications.json'
    applications = load_json(applications_path, [])
    applications.append(payload)
    save_json(applications_path, applications)

    return jsonify({'ok': True})


@app.route('/<path:path>')
def static_files(path):
    file_path = ENTRY_TEMPLATE_DIR / path
    if file_path.exists() and file_path.is_file():
        return send_from_directory(ENTRY_TEMPLATE_DIR, path)
    return ('Not Found', 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
