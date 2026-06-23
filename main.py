import os
from datetime import datetime, timedelta

from flask import jsonify, redirect, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from jinja2 import ChoiceLoader, FileSystemLoader

from backend.portal import main as portal
from backend.chat.indevidual_chat import app as chat


PROJECT_ROOT = portal.PROJECT_ROOT

app = portal.app
app.secret_key = os.getenv("SECRET_KEY") or app.secret_key or "dev_secret_key"
app.jinja_loader = ChoiceLoader(
    [
        FileSystemLoader(str(PROJECT_ROOT / "frontend-html" / "portal")),
        FileSystemLoader(str(PROJECT_ROOT / "frontend-html")),
    ]
)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

portal.config.update(
    {
        "calendar_url": os.getenv("CALENDAR_URL", "/calendar"),
        "chat_url": os.getenv("CHAT_URL", "/chat"),
        "videochat_url": os.getenv("VIDEOCHAT_URL", "/videochat"),
    }
)


def _json_response_error(message, status=400):
    return jsonify({"ok": False, "error": message}), status


@app.route("/portal")
def portal_index():
    return redirect("/")


@app.route("/entry")
def entry_index():
    return app.send_static_file("frontend-html/entry/index.html")


@app.route("/api/login", methods=["POST"])
def entry_api_login():
    data = request.get_json(silent=True) or {}
    key = (data.get("key") or "").strip()
    student = portal.load_json(PROJECT_ROOT / "resources-database" / "entry" / "students.json", {}).get(key)
    if not student:
        return jsonify({"ok": False})
    return jsonify({"ok": True, "name": student.get("name") or "Учень"})


@app.route("/api/apply", methods=["POST"])
def entry_api_apply():
    from backend.entry.server import send_email

    data = request.get_json(silent=True) or {}
    if not (data.get("studentName") or "").strip() or not (data.get("phone") or "").strip():
        return _json_response_error("missing_fields")

    payload = {
        "subject": data.get("subject", "Не вказано"),
        "teacher": data.get("teacher", "Не вказано"),
        "studentName": data.get("studentName", "Не вказано"),
        "studentClass": data.get("studentClass", "Не вказано"),
        "phone": data.get("phone", "Не вказано"),
        "message": data.get("message", "-"),
        "createdAt": datetime.utcnow().isoformat(),
    }

    entry_dir = PROJECT_ROOT / "resources-database" / "entry"
    config = portal.load_json(entry_dir / "config.json", {})
    if not config:
        return _json_response_error("missing_config")

    email_body = (
        "Нова заявка (MrBlackFox)\n\n"
        f"Предмет: {payload['subject']}\n"
        f"Викладач: {payload['teacher']}\n"
        f"Учень: {payload['studentName']}\n"
        f"Клас: {payload['studentClass']}\n"
        f"Телефон: {payload['phone']}\n"
        f"Повідомлення: {payload['message']}\n"
        f"Час (UTC): {payload['createdAt']}\n"
    )

    try:
        send_email("Нова заявка MrBlackFox", email_body, config)
    except Exception:
        return _json_response_error("email_failed")

    applications_path = entry_dir / "applications.json"
    applications = portal.load_json(applications_path, [])
    applications.append(payload)
    portal.save_json(applications_path, applications)
    return jsonify({"ok": True})


CALENDAR_DATA_FILE = PROJECT_ROOT / "resources-database" / "calendar" / "bookings.json"
TEACHERS = [
    "Олена Іваненко",
    "Максим Петренко",
    "Ірина Шевченко",
    "Андрій Коваленко",
    "Наталія Бондар",
]


def _load_bookings():
    return portal.load_json(CALENDAR_DATA_FILE, [])


def _save_bookings(bookings):
    portal.save_json(CALENDAR_DATA_FILE, bookings)


@app.route("/calendar")
def calendar_index():
    return render_template("calendar/index.html")


@app.route("/calendar/teacher")
def calendar_teacher():
    return render_template("calendar/teacher.html")


@app.route("/calendar/api/teachers")
def calendar_teachers():
    return jsonify({"teachers": TEACHERS})


@app.route("/calendar/api/bookings")
def calendar_bookings():
    return jsonify({"bookings": _load_bookings()})


@app.route("/calendar/api/book", methods=["POST"])
def calendar_book():
    payload = request.get_json(force=True)
    teacher = payload.get("teacher")
    date = payload.get("date")
    start_time = payload.get("time")
    duration_min = int(payload.get("duration", 60))

    if teacher not in TEACHERS:
        return _json_response_error("Невідомий вчитель")
    if duration_min not in (30, 45, 60, 90, 120):
        return _json_response_error("Некоректна тривалість")

    try:
        start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    except Exception:
        return _json_response_error("Некоректна дата або час")

    end_dt = start_dt + timedelta(minutes=duration_min)
    bookings = _load_bookings()
    for booking in bookings:
        if booking["teacher"] != teacher or booking["date"] != date:
            continue
        booking_start = datetime.strptime(f"{booking['date']} {booking['time']}", "%Y-%m-%d %H:%M")
        booking_end = booking_start + timedelta(minutes=int(booking["duration"]))
        if not (end_dt <= booking_start or start_dt >= booking_end):
            return _json_response_error("Час уже зайнятий", 409)

    bookings.append({"teacher": teacher, "date": date, "time": start_time, "duration": duration_min})
    _save_bookings(bookings)
    return jsonify({"ok": True})


@app.route("/chat")
def chat_index():
    user_log_id, _admin_log_id = chat.create_logs()
    return render_template("chat/index.html", log_id=user_log_id, role="user", stickers=chat.STICKERS)


@app.route("/chat/log/<log_id>")
def chat_user(log_id):
    if log_id not in chat.chat_history:
        chat.chat_history.setdefault(log_id, [])
        admin_log_id = chat.uuid.uuid4().hex[:8]
        while admin_log_id in chat.chat_history or admin_log_id in chat.admin_to_user or admin_log_id in chat.user_to_admin:
            admin_log_id = chat.uuid.uuid4().hex[:8]
        chat.admin_to_user[admin_log_id] = log_id
        chat.user_to_admin[log_id] = admin_log_id
        chat.save_store()
    return render_template("chat/index.html", log_id=log_id, role="user", stickers=chat.STICKERS)


@app.route("/chat/admin")
def chat_admin_logs():
    pairs = sorted(
        [(user, chat.user_to_admin.get(user, "")) for user in chat.chat_history.keys()],
        key=lambda item: item[0],
    )
    return render_template("chat/admin_list.html", pairs=pairs)


@app.route("/chat/admin/<log_id>")
def chat_admin(log_id):
    user_log_id = chat.resolve_room(log_id)
    if user_log_id not in chat.chat_history:
        chat.chat_history.setdefault(user_log_id, [])
        chat.save_store()
    return render_template("chat/index.html", log_id=user_log_id, role="admin", stickers=chat.STICKERS)


@app.route("/upload", methods=["POST"])
@app.route("/chat/upload", methods=["POST"])
def chat_upload():
    return chat.upload_files()


@socketio.on("join")
def chat_join(data):
    room = chat.resolve_room(data["room"])
    join_room(room)
    if room in chat.chat_history:
        emit("history", chat.chat_history[room])


@socketio.on("send_message")
def chat_message(data):
    room = chat.resolve_room(data["room"])
    text = str(data.get("text") or "").strip()
    files = chat.normalize_files(data.get("files") or [])
    sticker = str(data.get("sticker") or "").strip()
    if sticker and sticker not in chat.STICKER_URLS:
        sticker = ""
    if not text and not files and not sticker:
        return

    msg = {
        "text": text,
        "sender": data["role"],
        "time": data["time"],
        "files": files,
        "sticker": sticker,
    }
    chat.chat_history.setdefault(room, []).append(msg)
    chat.save_store()
    emit("receive_message", msg, room=room)


video_rooms = {}
video_sid_rooms = {}


@app.route("/videochat")
def videochat_index():
    return render_template("videochat/index.html")


@socketio.on("connect", namespace="/videochat")
def video_connect():
    room = (request.args.get("room") or "").strip()
    if not room:
        return False

    peers = video_rooms.setdefault(room, [])
    if len(peers) >= 2:
        return False

    peers.append(request.sid)
    video_sid_rooms[request.sid] = room
    join_room(room, namespace="/videochat")

    role = "offerer" if len(peers) == 2 else "waiter"
    emit("signal", {"type": "role", "role": role}, namespace="/videochat")
    if len(peers) == 2:
        emit("signal", {"type": "peer-joined"}, to=room, skip_sid=request.sid, namespace="/videochat")


@socketio.on("signal", namespace="/videochat")
def video_signal(message):
    room = video_sid_rooms.get(request.sid)
    if room:
        emit("signal", message, to=room, skip_sid=request.sid, namespace="/videochat")


@socketio.on("disconnect", namespace="/videochat")
def video_disconnect():
    room = video_sid_rooms.pop(request.sid, None)
    if not room:
        return
    leave_room(room, namespace="/videochat")
    peers = video_rooms.get(room, [])
    if request.sid in peers:
        peers.remove(request.sid)
    if peers:
        emit("signal", {"type": "peer-left"}, to=room, namespace="/videochat")
    else:
        video_rooms.pop(room, None)


@app.route("/healthz")
def healthz():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    socketio.run(app, host="0.0.0.0", port=port, debug=debug, allow_unsafe_werkzeug=True)
