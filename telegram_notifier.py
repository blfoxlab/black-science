import json
import os
import urllib.parse
import urllib.request
from html import escape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "resources-database" / "shared" / "config.json"


def _load_config() -> dict:
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def send_telegram_notification(text: str) -> bool:
    config = _load_config()
    token = os.getenv("TELEGRAM_TOKEN") or config.get("telegram_token", "")
    chat_id = (
        os.getenv("TELEGRAM_CHAT_ID")
        or os.getenv("TELEGRAM_GROUP_CHAT_ID")
        or os.getenv("TELEGRAM_ADMIN_ID")
        or config.get("telegram_chat_id", "")
        or config.get("telegram_group_chat_id", "")
        or config.get("telegram_admin_id", "")
    )

    if not token or not chat_id:
        return False

    safe_text = escape(str(text or "")).replace("\n", "\n")
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": safe_text,
            "parse_mode": "HTML",
        }
    ).encode("utf-8")
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        with urllib.request.urlopen(url, data=payload, timeout=10) as response:
            if response.status >= 400:
                return False
    except Exception:
        return False

    return True
