import json
import os
import re
import urllib.parse
import urllib.request
import uuid
from html import unescape
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import Markup, escape

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "resources-database" / "shared"
USERS_FILE = DATA_DIR / "users.json"
ROOMS_FILE = DATA_DIR / "chat_rooms.json"
CONFIG_FILE = DATA_DIR / "config.json"
TEST_PROGRESS_FILE = DATA_DIR / "test_progress.json"
CODE_PROGRESS_FILE = DATA_DIR / "code_progress.json"
COURSES_DIR = PROJECT_ROOT / "resources" / "cours"
PROGRAMMING_COURSE_ID = "frontend-backend-course"

DEFAULT_USERS = {
    "student1": {
        "password": "123",
        "role": "student",
        "name": "Олексій",
        "phone": "0991234567",
        "courses": ["math", "frontend-backend-course"],
    },
    "teacher1": {
        "password": "456",
        "role": "teacher",
        "name": "Олена Петрівна",
        "phone": "0997654321",
        "courses": ["math", "frontend-backend-course"],
    },
}

COURSE_TITLES = {
    "math": "Математика",
    "frontend-backend-course": "Фронтенд та основи бекенда",
}
COURSE_ORDER = {
    "math": 1,
    "frontend-backend-course": 2,
}
PROGRAMMING_TESTS = {
    "01-Вступ-до-веб-розробки": {
        "title": "Тест: вступ до веб-розробки",
        "description": "Перевірка базових ролей частин вебдодатку.",
        "questions": [
            {
                "text": "За що відповідає фронтенд?",
                "options": ["За видиму частину і взаємодію", "Тільки за базу даних", "Тільки за домен сайту"],
                "answer": 0,
            },
            {
                "text": "Що зазвичай робить бекенд?",
                "options": ["Малює CSS-анімації", "Обробляє запити й працює з даними", "Замінює HTML"],
                "answer": 1,
            },
        ],
    },
    "02-HTML-основа-верстки": {
        "title": "Тест: HTML",
        "description": "Семантика, структура і базові теги.",
        "questions": [
            {
                "text": "Який тег найкраще підходить для головного заголовка сторінки?",
                "options": ["p", "h1", "span"],
                "answer": 1,
            },
            {
                "text": "Для чого потрібен тег a?",
                "options": ["Для посилань", "Для зображень", "Для списків"],
                "answer": 0,
            },
        ],
    },
    "03-CSS-і-адаптивна-верстка": {
        "title": "Тест: CSS",
        "description": "Селектори, відступи й адаптивність.",
        "questions": [
            {
                "text": "Яка властивість задає внутрішні відступи?",
                "options": ["margin", "padding", "display"],
                "answer": 1,
            },
            {
                "text": "Що використовують для стилів під різні ширини екрана?",
                "options": ["@media", "@route", "@server"],
                "answer": 0,
            },
        ],
    },
    "04-JavaScript-база": {
        "title": "Тест: JavaScript",
        "description": "Функції, умови й повернення значень.",
        "questions": [
            {
                "text": "Що робить return у функції?",
                "options": ["Повертає результат", "Створює CSS", "Оголошує HTML-тег"],
                "answer": 0,
            },
            {
                "text": "Який оператор означає 'більше або дорівнює'?",
                "options": ["=>", ">=", "==>"],
                "answer": 1,
            },
        ],
    },
    "05-DOM-події-та-інтерактивність": {
        "title": "Тест: DOM",
        "description": "Елементи, події й зміна сторінки.",
        "questions": [
            {
                "text": "Який метод додає обробник події?",
                "options": ["addEventListener", "appendStyle", "setRoute"],
                "answer": 0,
            },
            {
                "text": "Що можна змінити через textContent?",
                "options": ["Адресу сервера", "Текст елемента", "Назву файлу"],
                "answer": 1,
            },
        ],
    },
    "06-Git-GitHub-та-робочий-процес": {
        "title": "Тест: Git",
        "description": "Репозиторій, стан і коміти.",
        "questions": [
            {
                "text": "Яка команда показує стан репозиторію?",
                "options": ["git status", "git paint", "git server"],
                "answer": 0,
            },
            {
                "text": "Для чого потрібен commit?",
                "options": ["Щоб зберегти зміни в історії", "Щоб відкрити браузер", "Щоб видалити CSS"],
                "answer": 0,
            },
        ],
    },
    "07-Основи-React": {
        "title": "Тест: React",
        "description": "Компоненти, JSX і props.",
        "questions": [
            {
                "text": "Що таке компонент React?",
                "options": ["Повторно використовувана частина інтерфейсу", "Тип бази даних", "HTTP-метод"],
                "answer": 0,
            },
            {
                "text": "Для чого потрібні props?",
                "options": ["Щоб передавати дані в компонент", "Щоб запускати сервер", "Щоб створювати SQL"],
                "answer": 0,
            },
        ],
    },
    "08-Стани-запити-та-форми-в-React": {
        "title": "Тест: стан і форми React",
        "description": "useState, форми й запити.",
        "questions": [
            {
                "text": "Який хук зберігає стан компонента?",
                "options": ["useState", "useRoute", "useSQL"],
                "answer": 0,
            },
            {
                "text": "Навіщо викликають preventDefault у submit?",
                "options": ["Щоб не перезавантажувати сторінку", "Щоб видалити input", "Щоб змінити порт"],
                "answer": 0,
            },
        ],
    },
    "09-Основи-бекенда": {
        "title": "Тест: основи бекенда",
        "description": "HTTP, JSON і відповідальність сервера.",
        "questions": [
            {
                "text": "Що таке JSON у вебдодатку?",
                "options": ["Формат обміну даними", "CSS-селектор", "Тип заголовка h1"],
                "answer": 0,
            },
            {
                "text": "Що сервер зазвичай повертає клієнту?",
                "options": ["Відповідь із даними або помилкою", "Тільки зображення", "Тільки пароль"],
                "answer": 0,
            },
        ],
    },
    "10-Node-js-та-Express": {
        "title": "Тест: Node.js та Express",
        "description": "Маршрути й відповіді сервера.",
        "questions": [
            {
                "text": "Для чого потрібен Express?",
                "options": ["Щоб створювати маршрути API", "Щоб писати HTML-теги", "Щоб замінити браузер"],
                "answer": 0,
            },
            {
                "text": "Що робить res.json?",
                "options": ["Відправляє JSON-відповідь", "Змінює CSS", "Створює Git-коміт"],
                "answer": 0,
            },
        ],
    },
    "11-REST-API-та-архітектура-застосунку": {
        "title": "Тест: REST API",
        "description": "Методи, ресурси й структура API.",
        "questions": [
            {
                "text": "Який HTTP-метод зазвичай читає список ресурсів?",
                "options": ["GET", "POST", "DELETE"],
                "answer": 0,
            },
            {
                "text": "Що означає /api/todos/:id?",
                "options": ["Маршрут з параметром id", "CSS-клас", "Назву бази даних"],
                "answer": 0,
            },
        ],
    },
    "12-Бази-даних-та-SQL": {
        "title": "Тест: SQL",
        "description": "Таблиці й базові запити.",
        "questions": [
            {
                "text": "Яке ключове слово вибирає дані?",
                "options": ["SELECT", "STYLE", "FETCHHTML"],
                "answer": 0,
            },
            {
                "text": "Для чого потрібен WHERE?",
                "options": ["Для умови фільтрації", "Для запуску сервера", "Для створення компонента"],
                "answer": 0,
            },
        ],
    },
    "13-Аутентифікація-та-безпека": {
        "title": "Тест: аутентифікація",
        "description": "Паролі, сесії й перевірка даних.",
        "questions": [
            {
                "text": "Як не можна зберігати пароль?",
                "options": ["Відкритим текстом", "У вигляді хешу", "З перевіркою довжини"],
                "answer": 0,
            },
            {
                "text": "Що треба робити з даними від користувача?",
                "options": ["Перевіряти", "Завжди довіряти", "Ігнорувати"],
                "answer": 0,
            },
        ],
    },
    "14-Фінальний-проєкт-та-деплой": {
        "title": "Тест: фінальний проєкт",
        "description": "MVP, змінні середовища й деплой.",
        "questions": [
            {
                "text": "Що таке MVP?",
                "options": ["Мінімальна робоча версія продукту", "Тип CSS-файлу", "SQL-команда"],
                "answer": 0,
            },
            {
                "text": "Де зазвичай зберігають секретні налаштування на сервері?",
                "options": ["У змінних середовища", "У публічному HTML", "У назві кнопки"],
                "answer": 0,
            },
        ],
    },
}


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def ensure_defaults() -> None:
    if not USERS_FILE.exists():
        save_json(USERS_FILE, DEFAULT_USERS)
    if not ROOMS_FILE.exists():
        save_json(ROOMS_FILE, {})
    if not CONFIG_FILE.exists():
        save_json(
            CONFIG_FILE,
            {
                "secret_key": "change_me",
                "telegram_token": "",
                "telegram_admin_id": "",
                "calendar_url": "http://localhost:5002",
                "chat_url": "http://localhost:5001",
                "videochat_url": "http://localhost:5003",
            },
        )
    if not TEST_PROGRESS_FILE.exists():
        save_json(TEST_PROGRESS_FILE, {})
    if not CODE_PROGRESS_FILE.exists():
        save_json(CODE_PROGRESS_FILE, {})


def load_config():
    cfg = load_json(CONFIG_FILE, {})
    return {
        "secret_key": os.getenv("SECRET_KEY") or cfg.get("secret_key") or "dev_secret_key",
        "telegram_token": os.getenv("TELEGRAM_TOKEN") or cfg.get("telegram_token", ""),
        "telegram_admin_id": os.getenv("TELEGRAM_ADMIN_ID") or cfg.get("telegram_admin_id", ""),
        "calendar_url": os.getenv("CALENDAR_URL") or cfg.get("calendar_url", "http://localhost:5002"),
        "chat_url": os.getenv("CHAT_URL") or cfg.get("chat_url", "http://localhost:5001"),
        "videochat_url": os.getenv("VIDEOCHAT_URL") or cfg.get("videochat_url", "http://localhost:5003"),
    }


ensure_defaults()
config = load_config()

app = Flask(
    __name__,
    static_folder=str(PROJECT_ROOT),
    static_url_path="/static",
    template_folder=str(PROJECT_ROOT / "frontend-html" / "portal"),
)
app.secret_key = config["secret_key"]


@app.route("/")
def index():
    return render_template("index.html")


def _send_telegram_message(text: str) -> None:
    token = config["telegram_token"]
    admin_id = config["telegram_admin_id"]
    if not token or not admin_id:
        raise RuntimeError("Telegram token or admin chat id is not configured")

    payload = urllib.parse.urlencode(
        {
            "chat_id": admin_id,
            "text": text,
            "parse_mode": "HTML",
        }
    ).encode("utf-8")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        with urllib.request.urlopen(url, data=payload, timeout=10) as response:
            if response.status >= 400:
                raise RuntimeError(f"Telegram returned HTTP {response.status}")
    except Exception as exc:
        raise RuntimeError("Telegram message was not sent") from exc


@app.route("/register", methods=["POST"])
def register():
    parent_name = (request.form.get("parent_name") or "").strip()
    student_name = (request.form.get("student_name") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    subject = (request.form.get("subject") or "").strip()

    msg = (
        "Нова заявка Black Science\n\n"
        f"Батьки: {escape(parent_name)}\n"
        f"Учень: {escape(student_name)}\n"
        f"Телефон: {escape(phone)}\n"
        f"Предмет: {escape(subject)}"
    )
    try:
        _send_telegram_message(msg)
    except RuntimeError:
        return render_template(
            "index.html",
            register_error="Заявку не надіслано: Telegram ще не налаштований.",
        )
    return render_template("index.html", register_ok=True)


@app.route("/login", methods=["POST"])
def login():
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    users = load_json(USERS_FILE, DEFAULT_USERS)
    user = users.get(username)

    if not user or user.get("password") != password:
        return render_template("index.html", login_error="Невірний логін або пароль")

    session["username"] = username
    session["role"] = user.get("role")
    if user.get("role") == "teacher":
        return redirect(url_for("teacher_dashboard"))
    return redirect(url_for("student_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def _require_role(role: str):
    if session.get("role") != role or "username" not in session:
        return False
    return True


def _get_or_create_room(username: str) -> str:
    rooms = load_json(ROOMS_FILE, {})
    if username not in rooms:
        rooms[username] = uuid.uuid4().hex[:8]
        save_json(ROOMS_FILE, rooms)
    return rooms[username]


def _course_title(course_id: str) -> str:
    return COURSE_TITLES.get(course_id, course_id.replace("-", " ").replace("_", " ").title())


def _read_md_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.stem.replace("_", " ").title()


def _available_courses():
    courses = []
    if not COURSES_DIR.exists():
        return courses
    course_dirs = sorted(
        (p for p in COURSES_DIR.iterdir() if p.is_dir()),
        key=lambda p: (COURSE_ORDER.get(p.name, 999), p.name),
    )
    for course_dir in course_dirs:
        lessons = sorted(p for p in course_dir.glob("*.md") if p.name not in {"plan.md", "README.md"})
        courses.append(
            {
                "id": course_dir.name,
                "title": _course_title(course_dir.name),
                "lessons_count": len(lessons),
                "has_plan": (course_dir / "plan.md").exists(),
            }
        )
    return courses


def _user_course_ids(user):
    course_ids = user.get("courses")
    if course_ids == "all":
        return [course["id"] for course in _available_courses()]
    if not course_ids:
        return ["math"]
    return course_ids


def _user_courses(user):
    allowed = set(_user_course_ids(user))
    return [course for course in _available_courses() if course["id"] in allowed]


def _current_user():
    users = load_json(USERS_FILE, DEFAULT_USERS)
    return users.get(session.get("username"), {})


def _dashboard_endpoint():
    return "teacher_dashboard" if session.get("role") == "teacher" else "student_dashboard"


def _require_course_access(course_id: str):
    if "username" not in session:
        return False
    return course_id in set(_user_course_ids(_current_user()))


def _course_lessons(course_id: str):
    course_dir = COURSES_DIR / course_id
    return [
        {
            "id": path.stem,
            "title": _read_md_title(path),
            "filename": path.name,
            "test": _lesson_test_summary(course_id, path.stem),
            "interactive": _lesson_interactive_summary(course_id, path.stem),
        }
        for path in sorted(course_dir.glob("*.md"))
        if path.name not in {"plan.md", "README.md"}
    ]


def _interactive_path(course_id: str) -> Path:
    return COURSES_DIR / course_id / "interactive.json"


def _load_interactive_course(course_id: str) -> dict:
    path = _interactive_path(course_id)
    if not path.exists():
        return {"lessons": {}}
    data = load_json(path, {})
    return {"lessons": data.get("lessons", {})}


def _load_code_challenge(course_id: str, lesson_id: str):
    lesson = _load_interactive_course(course_id).get("lessons", {}).get(lesson_id, {})
    challenge = lesson.get("challenge")
    if not challenge:
        return None
    return {
        "id": challenge.get("id") or lesson_id,
        "title": challenge.get("title") or "Практика з кодом",
        "brief": lesson.get("brief", ""),
        "task": challenge.get("task") or "",
        "language": challenge.get("language") or "html",
        "starter": challenge.get("starter") or "",
        "checks": challenge.get("checks", []),
        "hint": challenge.get("hint") or "",
    }


def _all_code_progress():
    return load_json(CODE_PROGRESS_FILE, {})


def _code_progress(username: str, course_id: str, lesson_id: str):
    return (
        _all_code_progress()
        .get(username, {})
        .get(course_id, {})
        .get(lesson_id)
    )


def _save_code_progress(username: str, course_id: str, lesson_id: str, result: dict) -> None:
    progress = _all_code_progress()
    progress.setdefault(username, {}).setdefault(course_id, {})[lesson_id] = result
    save_json(CODE_PROGRESS_FILE, progress)


def _lesson_interactive_summary(course_id: str, lesson_id: str):
    lesson = _load_interactive_course(course_id).get("lessons", {}).get(lesson_id, {})
    challenge = lesson.get("challenge")
    progress = _code_progress(session.get("username", ""), course_id, lesson_id) if challenge else None
    return {
        "brief": lesson.get("brief", ""),
        "challenge_exists": bool(challenge),
        "progress": progress,
    }


def _check_code_submission(challenge: dict, code: str) -> dict:
    checks = []
    for check in challenge.get("checks", []):
        kind = check.get("type", "contains")
        value = check.get("value", "")
        label = check.get("label") or value or "Перевірка"
        flags = re.IGNORECASE | re.MULTILINE

        if kind == "contains":
            passed = value.lower() in code.lower()
        elif kind == "not_contains":
            passed = value.lower() not in code.lower()
        elif kind == "regex":
            passed = bool(re.search(value, code, flags))
        elif kind == "min_length":
            passed = len(code.strip()) >= int(value or 0)
        else:
            passed = False

        checks.append({"label": label, "passed": passed})

    passed_count = sum(1 for item in checks if item["passed"])
    total = len(checks)
    return {
        "passed": total > 0 and passed_count == total,
        "score": passed_count,
        "total": total,
        "percent": round((passed_count / total) * 100) if total else 0,
        "checks": checks,
        "code": code,
    }


def _test_path(course_id: str, lesson_id: str) -> Path:
    return COURSES_DIR / course_id / "tests" / f"{lesson_id}.json"


def _load_test(course_id: str, lesson_id: str):
    test_path = _test_path(course_id, lesson_id)
    if test_path.exists():
        data = load_json(test_path, {})
    elif course_id == PROGRAMMING_COURSE_ID:
        data = PROGRAMMING_TESTS.get(lesson_id, {})
    else:
        return None
    questions = data.get("questions", [])
    if not questions:
        return None
    return {
        "id": data.get("id") or lesson_id,
        "title": data.get("title") or f"Тест: {lesson_id}",
        "description": data.get("description") or "",
        "questions": questions,
    }


def _all_test_progress():
    return load_json(TEST_PROGRESS_FILE, {})


def _test_progress(username: str, course_id: str, lesson_id: str):
    return (
        _all_test_progress()
        .get(username, {})
        .get(course_id, {})
        .get(lesson_id)
    )


def _save_test_progress(username: str, course_id: str, lesson_id: str, result: dict) -> None:
    progress = _all_test_progress()
    progress.setdefault(username, {}).setdefault(course_id, {})[lesson_id] = result
    save_json(TEST_PROGRESS_FILE, progress)


def _lesson_test_summary(course_id: str, lesson_id: str):
    test = _load_test(course_id, lesson_id)
    if not test:
        return {"exists": False}
    progress = _test_progress(session.get("username", ""), course_id, lesson_id)
    return {
        "exists": True,
        "questions_count": len(test["questions"]),
        "progress": progress,
    }


def _score_test(test: dict, form) -> dict:
    answers = []
    correct = 0
    for index, question in enumerate(test["questions"]):
        submitted = form.get(f"q{index}")
        try:
            selected = int(submitted)
        except (TypeError, ValueError):
            selected = None
        answer = question.get("answer")
        is_correct = selected == answer
        if is_correct:
            correct += 1
        answers.append(
            {
                "selected": selected,
                "correct": answer,
                "is_correct": is_correct,
            }
        )
    total = len(test["questions"])
    percent = round((correct / total) * 100) if total else 0
    return {
        "passed": True,
        "score": correct,
        "total": total,
        "percent": percent,
        "answers": answers,
    }


def _inline_markdown(text: str, render_mode: str = "default") -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", str(text))
    text = re.sub(
        r"`([^`]+)`",
        lambda match: _render_inline_code(match, render_mode),
        text,
    )
    return text


def _looks_like_math(text: str) -> bool:
    math_tokens = (
        "=", "+", "-", "/", "\\", "^", "_", "√", "∫", "π", "sin", "cos", "tg",
        "ctg", "log", "ln", "arcsin", "arccos", "arctg", "lim", "F(", "f(",
    )
    return any(token in text for token in math_tokens)


_MATH_WORD_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
    "0123456789"
)
_MATH_OPERATORS = set("=+-−*·×,;:<>|&")
_OPENING_GROUPS = "({["
_CLOSING_GROUPS = ")}]"
_GROUP_PAIRS = {")": "(", "}": "{", "]": "["}
_GROUP_ENDS = {"(": ")", "{": "}", "[": "]"}


def _wrap_parenthesized(text: str, marker: str, wrapper) -> str:
    result = []
    index = 0
    needle = marker + "("
    while index < len(text):
        if not text.startswith(needle, index):
            result.append(text[index])
            index += 1
            continue

        start = index + len(needle)
        end = _group_end(text, start - 1)
        if end is None:
            result.append(marker)
            index += len(marker)
            continue

        result.append(wrapper(text[start:end - 1].strip()))
        index = end
    return "".join(result)


def _texify_powers_and_indexes(text: str) -> str:
    superscripts = {
        "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
        "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    }
    for source, target in superscripts.items():
        text = text.replace(source, f"^{target}")
    text = _wrap_parenthesized(text, "^", lambda value: f"^{{{value}}}")
    text = re.sub(r"\^(-?\d+|[A-Za-zА-Яа-яҐґЄєІіЇї]+)", r"^{\1}", text)
    text = _wrap_parenthesized(text, "_", lambda value: f"_{{{value}}}")
    text = re.sub(r"_(-?\d+|[A-Za-zА-Яа-яҐґЄєІіЇї]+)", r"_{\1}", text)
    return text


def _texify_roots(text: str) -> str:
    text = re.sub(r"([A-Za-z0-9]+)√\(([^()\n]+)\)", r"\\sqrt[\1]{\2}", text)
    text = re.sub(r"([A-Za-z0-9]+)√([A-Za-z0-9]+)", r"\\sqrt[\1]{\2}", text)
    text = text.replace("√", r"\sqrt")
    text = _wrap_parenthesized(text, r"\sqrt", lambda value: rf"\sqrt{{{value}}}")
    text = re.sub(r"\\sqrt([A-Za-zА-Яа-яҐґЄєІіЇї0-9]+)", r"\\sqrt{\1}", text)
    return text


def _group_end(text: str, start: int) -> int | None:
    if start >= len(text) or text[start] not in _OPENING_GROUPS:
        return None
    depth = 1
    cursor = start + 1
    while cursor < len(text):
        if text[cursor] == text[start]:
            depth += 1
        elif text[cursor] == _GROUP_ENDS[text[start]]:
            depth -= 1
            if depth == 0:
                return cursor + 1
        cursor += 1
    return None


def _command_start(text: str, index: int) -> int:
    cursor = index
    while cursor >= 0 and text[cursor].isalpha():
        cursor -= 1
    if cursor >= 0 and text[cursor] == "\\":
        return cursor
    return index + 1


def _find_left_token(text: str, slash_index: int) -> int | None:
    end = slash_index - 1
    while end >= 0 and text[end].isspace():
        end -= 1
    if end < 0:
        return None

    if text[end] in _CLOSING_GROUPS:
        depth = 1
        cursor = end - 1
        while cursor >= 0:
            if text[cursor] == text[end]:
                depth += 1
            elif text[cursor] == _GROUP_PAIRS[text[end]]:
                depth -= 1
                if depth == 0:
                    start = cursor
                    if start > 0 and text[start - 1] in "^_":
                        return _find_left_token(text, start - 1)
                    return _command_start(text, start - 1)
            cursor -= 1
        return None

    cursor = end
    while cursor >= 0 and text[cursor] in ("\\" + _MATH_WORD_CHARS):
        cursor -= 1
    if cursor >= 0 and text[cursor] in "^_":
        return _find_left_token(text, cursor)
    return cursor + 1


def _find_right_operand(text: str, slash_index: int) -> int | None:
    start = slash_index + 1
    while start < len(text) and text[start].isspace():
        start += 1
    if start >= len(text):
        return None

    if text[start] in _OPENING_GROUPS:
        return _group_end(text, start)

    cursor = start
    while cursor < len(text) and text[cursor] in ("\\" + _MATH_WORD_CHARS):
        cursor += 1
    if text[start] == "\\":
        if cursor < len(text) and text[cursor] == "[":
            cursor = _group_end(text, cursor) or cursor
        if cursor < len(text) and text[cursor] == "{":
            cursor = _group_end(text, cursor) or cursor

    while cursor < len(text) and text[cursor] in "_^":
        cursor += 1
        if cursor < len(text) and text[cursor] in _OPENING_GROUPS:
            group_end = _group_end(text, cursor)
            if group_end is None:
                break
            cursor = group_end
        else:
            while cursor < len(text) and text[cursor] in ("\\" + _MATH_WORD_CHARS):
                cursor += 1

    if cursor < len(text) and text[cursor] == "(":
        cursor = _group_end(text, cursor) or cursor
    return cursor


def _is_spaced_fraction(text: str, slash_index: int) -> bool:
    return (
        slash_index > 0
        and slash_index + 1 < len(text)
        and text[slash_index - 1].isspace()
        and text[slash_index + 1].isspace()
    )


def _find_left_phrase(text: str, slash_index: int) -> int | None:
    end = slash_index - 1
    while end >= 0 and text[end].isspace():
        end -= 1
    if end < 0:
        return None

    depth = 0
    cursor = end
    while cursor >= 0:
        char = text[cursor]
        if char in _CLOSING_GROUPS:
            depth += 1
        elif char in _OPENING_GROUPS:
            depth -= 1
        elif depth == 0 and char in _MATH_OPERATORS:
            return cursor + 1
        cursor -= 1
    return 0


def _find_right_phrase(text: str, slash_index: int) -> int | None:
    start = slash_index + 1
    while start < len(text) and text[start].isspace():
        start += 1
    if start >= len(text):
        return None

    depth = 0
    cursor = start
    while cursor < len(text):
        char = text[cursor]
        if char in _OPENING_GROUPS:
            depth += 1
        elif char in _CLOSING_GROUPS:
            depth -= 1
        elif depth == 0 and char in _MATH_OPERATORS:
            break
        cursor += 1
    return cursor


def _strip_group(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == "(" and text[-1] == ")":
        return text[1:-1].strip()
    return text


def _texify_simple_fractions(text: str) -> str:
    index = 0
    while index < len(text):
        slash_index = text.find("/", index)
        if slash_index == -1:
            break

        if _is_spaced_fraction(text, slash_index):
            left = _find_left_phrase(text, slash_index)
            right = _find_right_phrase(text, slash_index)
        else:
            left = _find_left_token(text, slash_index)
            right = _find_right_operand(text, slash_index)

        if left is None or right is None or left == slash_index or right == slash_index + 1:
            index = slash_index + 1
            continue
        numerator = _strip_group(text[left:slash_index])
        denominator = _strip_group(text[slash_index + 1:right])
        text = f"{text[:left]}\\frac{{{numerator}}}{{{denominator}}}{text[right:]}"
        index = left + len(r"\frac") + len(numerator) + len(denominator) + 4
    return text


def _normalize_math_shortcuts(text: str) -> str:
    text = re.sub(r"(?<![A-Za-zА-Яа-яҐґЄєІіЇї0-9\\])/(?:pin|pi)\b", r"\\pi ", text)
    text = re.sub(r"\\pin\b", r"\\pi ", text)
    text = re.sub(r"\\pi\b", r"\\pi ", text)
    return text


def _texify_functions(text: str) -> str:
    functions = {
        "arcsin": r"\arcsin",
        "arccos": r"\arccos",
        "arctg": r"\operatorname{arctg}",
        "ctg": r"\operatorname{ctg}",
        "cosec": r"\operatorname{cosec}",
        "sec": r"\operatorname{sec}",
        "cos": r"\cos",
        "lim": r"\lim",
        "log": r"\log",
        "sin": r"\sin",
        "tg": r"\operatorname{tg}",
        "ln": r"\ln",
    }
    pattern = r"(?<![\\A-Za-z])(" + "|".join(sorted(functions, key=len, reverse=True)) + r")(?![A-Za-z])"
    return re.sub(pattern, lambda match: functions[match.group(1)], text)


def _texify_symbols(text: str) -> str:
    replacements = {
        "α": r"\alpha ",
        "β": r"\beta ",
        "γ": r"\gamma ",
        "δ": r"\delta ",
        "θ": r"\theta ",
        "λ": r"\lambda ",
        "μ": r"\mu ",
        "π": r"\pi ",
        "φ": r"\varphi ",
        "°": r"^\circ",
        "∫": r"\int ",
        "∞": r"\infty ",
        "<=>": r"\Longleftrightarrow",
        "!=": r"\ne",
        ">=": r"\ge",
        "<=": r"\le",
        "->": r"\to",
        "...": r"\ldots",
        "*": r"\cdot ",
        "±": r"\pm",
        "·": r"\cdot ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _tex_escape_text(value: str) -> str:
    return (
        value.replace("\\", r"\textbackslash{}")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("%", r"\%")
        .replace("&", r"\&")
        .replace("#", r"\#")
        .replace("_", r"\_")
    )


def _texify_text_phrases(text: str) -> str:
    word = r"[А-Яа-яҐґЄєІіЇїЙй'’\-]+"
    pattern = rf"{word}(?:\s+{word})*"

    def replace(match: re.Match) -> str:
        prefix = text[max(0, match.start() - 6):match.start()]
        if prefix.endswith(r"\text{") or prefix.endswith(r"\mathrm{"):
            return match.group(0)
        return r"\text{" + _tex_escape_text(match.group(0)) + "}"

    return re.sub(pattern, replace, text)


def _math_to_tex(text: str) -> str:
    text = str(text)
    text = _normalize_math_shortcuts(text)
    text = _texify_symbols(text)
    text = _texify_roots(text)
    text = _texify_powers_and_indexes(text)
    text = _texify_functions(text)
    text = _texify_simple_fractions(text)
    text = _texify_text_phrases(text)
    return str(escape(text))


def _math_block_to_tex(text: str) -> str:
    lines = [_math_to_tex(line.strip()) for line in text.splitlines() if line.strip()]
    if len(lines) <= 1:
        body = lines[0] if lines else ""
    else:
        body = r"\begin{aligned}" + r" \\ ".join(lines) + r"\end{aligned}"
    return f"$${body}$$"


def _normalize_math_block(content: str) -> str:
    text = content.strip()
    if text.startswith("$$") and text.endswith("$$"):
        text = text[2:-2].strip()
    return _math_block_to_tex(text)


def _render_inline_code(match: re.Match, render_mode: str = "default") -> str:
    value = unescape(match.group(1))
    if render_mode == "math" and _looks_like_math(value):
        return rf"\({_math_to_tex(value)}\)"
    return f"<code>{escape(value)}</code>"


def _course_render_mode(course_id: str) -> str:
    if course_id == "math":
        return "math"
    if course_id == "frontend-backend-course":
        return "programming"
    return "default"


def _markdown_to_html(markdown_text: str, render_mode: str = "default") -> Markup:
    html = []
    lines = markdown_text.splitlines()
    in_ul = False
    in_ol = False
    in_table = False
    in_math = False
    math_lines = []
    in_code = False
    code_lines = []
    code_lang = ""

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html.append("</ul>")
            in_ul = False
        if in_ol:
            html.append("</ol>")
            in_ol = False

    def close_table():
        nonlocal in_table
        if in_table:
            html.append("</tbody></table>")
            in_table = False

    def close_math():
        nonlocal in_math, math_lines
        if in_math:
            content = "\n".join(math_lines)
            html.append(f"<div class=\"math-block\">{_normalize_math_block(content)}</div>")
            in_math = False
            math_lines = []

    def close_code():
        nonlocal in_code, code_lines, code_lang
        if in_code:
            content = "\n".join(code_lines).strip("\n")
            if render_mode == "math" and content and code_lang in {"", "text", "math"} and _looks_like_math(content):
                html.append(f"<div class=\"math-block\">{_normalize_math_block(content)}</div>")
            else:
                lang = escape(code_lang.upper()) if code_lang else "CODE"
                html.append(
                    f"<div class=\"code-block\" data-lang=\"{lang}\">"
                    f"<pre><code>{escape(content)}</code></pre>"
                    "</div>"
                )
            in_code = False
            code_lines = []
            code_lang = ""

    for line in lines:
        raw = line.strip()
        if in_code:
            if raw.startswith("```"):
                close_code()
            else:
                code_lines.append(line)
            continue

        if raw.startswith("```"):
            close_lists()
            close_table()
            in_code = True
            code_lines = []
            code_info = raw[3:].strip().split(maxsplit=1)
            code_lang = code_info[0] if code_info else ""
            continue

        if in_math:
            math_lines.append(line)
            if raw.endswith("$$"):
                close_math()
            continue

        if raw.startswith("$$"):
            close_lists()
            close_table()
            in_math = True
            math_lines = [line]
            if raw.endswith("$$") and len(raw) > 2:
                close_math()
            continue

        if not raw:
            close_lists()
            close_table()
            continue

        if raw.startswith("|") and raw.endswith("|"):
            close_lists()
            cells = [cell.strip() for cell in raw.strip("|").split("|")]
            if all(set(cell) <= {"-", ":"} and "-" in cell for cell in cells):
                continue
            if not in_table:
                html.append("<table><tbody>")
                in_table = True
            tag = "th" if not any("<tr>" in item for item in html[-1:]) else "td"
            html.append(
                "<tr>"
                + "".join(f"<{tag}>{_inline_markdown(cell, render_mode)}</{tag}>" for cell in cells)
                + "</tr>"
            )
            continue

        close_table()

        heading = re.match(r"^(#{1,4})\s+(.+)$", raw)
        if heading:
            close_lists()
            level = len(heading.group(1))
            html.append(f"<h{level}>{_inline_markdown(heading.group(2), render_mode)}</h{level}>")
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", raw)
        if ordered:
            if in_ul:
                html.append("</ul>")
                in_ul = False
            if not in_ol:
                html.append("<ol>")
                in_ol = True
            html.append(f"<li>{_inline_markdown(ordered.group(1), render_mode)}</li>")
            continue

        if raw.startswith("- "):
            if in_ol:
                html.append("</ol>")
                in_ol = False
            if not in_ul:
                html.append("<ul>")
                in_ul = True
            html.append(f"<li>{_inline_markdown(raw[2:], render_mode)}</li>")
            continue

        close_lists()
        html.append(f"<p>{_inline_markdown(raw, render_mode)}</p>")

    close_lists()
    close_table()
    close_math()
    close_code()
    return Markup("\n".join(html))


@app.route("/student")
def student_dashboard():
    if not _require_role("student"):
        return redirect(url_for("index"))

    users = load_json(USERS_FILE, DEFAULT_USERS)
    user = users.get(session.get("username"), {})
    room_id = _get_or_create_room(session.get("username"))

    return render_template(
        "student.html",
        user=user,
        courses=_user_courses(user),
        calendar_url=config["calendar_url"],
        chat_url=f"{config['chat_url'].rstrip('/')}/log/{room_id}",
        video_url=config["videochat_url"],
    )


@app.route("/teacher")
def teacher_dashboard():
    if not _require_role("teacher"):
        return redirect(url_for("index"))

    users = load_json(USERS_FILE, DEFAULT_USERS)
    user = users.get(session.get("username"), {})

    return render_template(
        "teacher.html",
        user=user,
        courses=_user_courses(user),
        calendar_url=f"{config['calendar_url'].rstrip('/')}/teacher",
        chat_url=f"{config['chat_url'].rstrip('/')}/admin",
        video_url=config["videochat_url"],
    )


@app.route("/courses")
def courses():
    if "username" not in session:
        return redirect(url_for("index"))
    user = _current_user()
    return render_template(
        "courses.html",
        user=user,
        courses=_user_courses(user),
        dashboard_endpoint=_dashboard_endpoint(),
    )


@app.route("/courses/<course_id>")
def course_detail(course_id):
    if not _require_course_access(course_id):
        return redirect(url_for("courses"))
    course = {
        "id": course_id,
        "title": _course_title(course_id),
        "has_plan": (COURSES_DIR / course_id / "plan.md").exists(),
    }
    return render_template(
        "course.html",
        course=course,
        lessons=_course_lessons(course_id),
        dashboard_endpoint=_dashboard_endpoint(),
    )


@app.route("/courses/<course_id>/plan")
def course_plan(course_id):
    if not _require_course_access(course_id):
        return redirect(url_for("courses"))
    plan_path = COURSES_DIR / course_id / "plan.md"
    if not plan_path.exists():
        return redirect(url_for("course_detail", course_id=course_id))
    text = plan_path.read_text(encoding="utf-8")
    return render_template(
        "lesson.html",
        course={"id": course_id, "title": _course_title(course_id)},
        title=_read_md_title(plan_path),
        content=_markdown_to_html(text, _course_render_mode(course_id)),
        render_mode=_course_render_mode(course_id),
        back_url=url_for("course_detail", course_id=course_id),
        back_label="До курсу",
    )


@app.route("/courses/<course_id>/lesson/<lesson_id>")
def course_lesson(course_id, lesson_id):
    if not _require_course_access(course_id):
        return redirect(url_for("courses"))
    lessons = {lesson["id"] for lesson in _course_lessons(course_id)}
    if lesson_id not in lessons:
        return redirect(url_for("course_detail", course_id=course_id))
    lesson_path = COURSES_DIR / course_id / f"{lesson_id}.md"
    text = lesson_path.read_text(encoding="utf-8")
    return render_template(
        "lesson.html",
        course={"id": course_id, "title": _course_title(course_id)},
        title=_read_md_title(lesson_path),
        content=_markdown_to_html(text, _course_render_mode(course_id)),
        render_mode=_course_render_mode(course_id),
        back_url=url_for("course_detail", course_id=course_id),
        back_label="До курсу",
    )


@app.route("/courses/<course_id>/lesson/<lesson_id>/test", methods=["GET", "POST"])
def course_lesson_test(course_id, lesson_id):
    if not _require_course_access(course_id):
        return redirect(url_for("courses"))
    lessons = {lesson["id"] for lesson in _course_lessons(course_id)}
    if lesson_id not in lessons:
        return redirect(url_for("course_detail", course_id=course_id))

    test = _load_test(course_id, lesson_id)
    if not test:
        return redirect(url_for("course_lesson", course_id=course_id, lesson_id=lesson_id))

    username = session.get("username")
    result = _test_progress(username, course_id, lesson_id)
    if request.method == "POST":
        result = _score_test(test, request.form)
        _save_test_progress(username, course_id, lesson_id, result)

    return render_template(
        "test.html",
        course={"id": course_id, "title": _course_title(course_id)},
        lesson_id=lesson_id,
        test=test,
        result=result,
        back_url=url_for("course_detail", course_id=course_id),
        lesson_url=url_for("course_lesson", course_id=course_id, lesson_id=lesson_id),
    )


@app.route("/courses/<course_id>/lesson/<lesson_id>/practice", methods=["GET", "POST"])
def course_lesson_practice(course_id, lesson_id):
    if not _require_course_access(course_id):
        return redirect(url_for("courses"))
    lessons = {lesson["id"] for lesson in _course_lessons(course_id)}
    if lesson_id not in lessons:
        return redirect(url_for("course_detail", course_id=course_id))

    challenge = _load_code_challenge(course_id, lesson_id)
    if not challenge:
        return redirect(url_for("course_lesson", course_id=course_id, lesson_id=lesson_id))

    username = session.get("username")
    result = _code_progress(username, course_id, lesson_id)
    code = result.get("code") if result else challenge["starter"]

    if request.method == "POST":
        code = request.form.get("code") or ""
        result = _check_code_submission(challenge, code)
        _save_code_progress(username, course_id, lesson_id, result)

    return render_template(
        "practice.html",
        course={"id": course_id, "title": _course_title(course_id)},
        lesson_id=lesson_id,
        challenge=challenge,
        code=code,
        result=result,
        back_url=url_for("course_detail", course_id=course_id),
        lesson_url=url_for("course_lesson", course_id=course_id, lesson_id=lesson_id),
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
