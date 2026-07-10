import json
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[1]

app = Flask(
    __name__,
    static_folder=str(PROJECT_ROOT),
    static_url_path="/static",
    template_folder=str(PROJECT_ROOT / "frontend-html" / "calendar"),
)

DATA_FILE = PROJECT_ROOT / "resources-database" / "calendar" / "bookings.json"
LOCK = threading.Lock()

DEFAULT_TEACHERS = [
    "Олена Іваненко",
    "Максим Петренко",
    "Ірина Шевченко",
    "Андрій Коваленко",
    "Наталія Бондар",
]


def _load_bookings():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _teacher_names():
    users_file = PROJECT_ROOT / "resources-database" / "shared" / "users.json"
    if users_file.exists():
        try:
            users = json.loads(users_file.read_text(encoding="utf-8"))
            teachers = [user.get("name") for user in users.values() if user.get("role") == "teacher" and user.get("name")]
            if teachers:
                return sorted(teachers)
        except json.JSONDecodeError:
            pass
    return sorted(DEFAULT_TEACHERS)


def _save_bookings(bookings):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)
    tmp.replace(DATA_FILE)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/teacher")
def teacher():
    return render_template("teacher.html")


@app.route("/api/teachers")
def teachers():
    return jsonify({"teachers": _teacher_names()})


@app.route("/calendar/api/teachers")
def calendar_api_teachers():
    return jsonify({"teachers": _teacher_names()})


@app.route("/api/bookings")
def bookings():
    with LOCK:
        data = _load_bookings()
    return jsonify({"bookings": data})


@app.route("/calendar/api/bookings")
def calendar_api_bookings():
    with LOCK:
        data = _load_bookings()
    return jsonify({"bookings": data})


@app.route("/api/book", methods=["POST"])
def book():
    return _book_handler()


@app.route("/calendar/api/book", methods=["POST"])
def calendar_book():
    return _book_handler()


def _book_handler():
    payload = request.get_json(force=True)
    teacher = payload.get("teacher")
    date = payload.get("date")  # YYYY-MM-DD
    start_time = payload.get("time")  # HH:MM
    duration_min = int(payload.get("duration", 60))

    if teacher not in _teacher_names():
        return jsonify({"ok": False, "error": "Невідомий вчитель"}), 400

    try:
        start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    except Exception:
        return jsonify({"ok": False, "error": "Некоректна дата або час"}), 400

    if duration_min not in (30, 45, 60, 90, 120):
        return jsonify({"ok": False, "error": "Некоректна тривалість"}), 400

    end_dt = start_dt + timedelta(minutes=duration_min)

    with LOCK:
        data = _load_bookings()
        # check conflicts
        for b in data:
            if b["teacher"] != teacher or b["date"] != date:
                continue
            b_start = datetime.strptime(f"{b['date']} {b['time']}", "%Y-%m-%d %H:%M")
            b_end = b_start + timedelta(minutes=int(b["duration"]))
            if not (end_dt <= b_start or start_dt >= b_end):
                return jsonify({"ok": False, "error": "Час уже зайнятий"}), 409

        data.append({
            "teacher": teacher,
            "date": date,
            "time": start_time,
            "duration": duration_min,
        })
        _save_bookings(data)

    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5002"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
