import json
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "resources-database" / "shared" / "config.json"


def main() -> None:
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    token = config.get("telegram_token", "")
    if not token:
        raise SystemExit("Telegram token is not configured.")

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    for update in reversed(data.get("result", [])):
        message = (
            update.get("message")
            or update.get("edited_message")
            or update.get("channel_post")
            or {}
        )
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id:
            config["telegram_admin_id"] = str(chat_id)
            CONFIG_FILE.write_text(
                json.dumps(config, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"Telegram chat id saved: {chat_id}")
            return

    print("No Telegram chat found. Send any message to the bot, then run this script again.")


if __name__ == "__main__":
    main()
