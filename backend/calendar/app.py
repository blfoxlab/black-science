import json
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

app = Flask(
    __name__,
    static_folder=str(PROJECT_ROOT),
    static_url_path="/static",
    template_folder=str(PROJECT_ROOT / "frontend-html" / "calendar"),
)

DATA_FILE = PROJECT_ROOT / "resources-database" / "calendar" / "bookings.json"
LOCK = threading.Lock()

TEACHERS = [
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
    return jsonify({"teachers": TEACHERS})


@app.route("/api/bookings")
def bookings():
    with LOCK:
        data = _load_bookings()
    return jsonify({"bookings": data})


@app.route("/api/book", methods=["POST"])
def book():
    payload = request.get_json(force=True)
    teacher = payload.get("teacher")
    date = payload.get("date")  # YYYY-MM-DD
    start_time = payload.get("time")  # HH:MM
    duration_min = int(payload.get("duration", 60))

    if teacher not in TEACHERS:
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
