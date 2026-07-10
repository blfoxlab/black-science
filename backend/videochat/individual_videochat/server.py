import json
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import sys
sys.path.append(str(Path(__file__).resolve().parents[3]))
from telegram_notifier import send_telegram_notification
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent.parent
STATIC_DIR = PROJECT_ROOT
INDEX_FILE = PROJECT_ROOT / "frontend-html" / "videochat" / "index.html"
CERTS_DIR = PROJECT_ROOT / "resources" / "videochat" / "certs"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

rooms: Dict[str, List[WebSocket]] = {}


def _room_peers(room: str) -> List[WebSocket]:
    return rooms.setdefault(room, [])


async def _broadcast(room: str, message: dict, sender: WebSocket | None = None) -> None:
    payload = json.dumps(message)
    for ws in list(_room_peers(room)):
        if sender is not None and ws is sender:
            continue
        try:
            await ws.send_text(payload)
        except Exception:
            # Ignore; disconnect cleanup will handle dead sockets
            pass


@app.get("/")
async def index():
    with INDEX_FILE.open("r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    room = ws.query_params.get("room")
    if not room:
        await ws.close(code=4001)
        return

    peers = _room_peers(room)
    if len(peers) >= 2:
        await ws.close(code=4002)
        return

    await ws.accept()
    peers.append(ws)

    # Assign role: second peer becomes offerer, first waits
    role = "offerer" if len(peers) == 2 else "waiter"
    await ws.send_text(json.dumps({"type": "role", "role": role}))
    if len(peers) == 2:
        await _broadcast(room, {"type": "peer-joined"}, sender=ws)
        send_telegram_notification(f"🎥 Хтось зайшов у відеодзвінок\nКімната: {room}\nСтатус: з'єднання встановлено")

    try:
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue
            # relay all signaling messages to the other peer
            await _broadcast(room, msg, sender=ws)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        peers = _room_peers(room)
        if ws in peers:
            peers.remove(ws)
        if not peers:
            rooms.pop(room, None)
        else:
            await _broadcast(room, {"type": "peer-left"})


if __name__ == "__main__":
    import uvicorn
    import subprocess
    import sys
    import os

    host = os.getenv("VIDEOCHAT_HOST", "127.0.0.1")
    port = int(os.getenv("VIDEOCHAT_PORT", "5003"))
    use_ssl = os.getenv("VIDEOCHAT_USE_SSL", "0").lower() in {"1", "true", "yes"}
    cert_host = os.getenv("VIDEOCHAT_CERT_HOST", host)

    ssl_keyfile = None
    ssl_certfile = None

    if use_ssl:
        cert_path = CERTS_DIR / "cert.pem"
        key_path = CERTS_DIR / "key.pem"
        if not cert_path.exists() or not key_path.exists():
            cert_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(
                    [
                        "openssl",
                        "req",
                        "-x509",
                        "-newkey",
                        "rsa:2048",
                        "-nodes",
                        "-keyout",
                        str(key_path),
                        "-out",
                        str(cert_path),
                        "-days",
                        "365",
                        "-subj",
                        f"/CN={cert_host}",
                    ],
                    check=True,
                )
            except Exception as exc:
                print("Не вдалося створити SSL-сертифікат:", exc)
                print(f"Очікувані шляхи: {cert_path} і {key_path}")
                sys.exit(1)
        ssl_keyfile = str(key_path)
        ssl_certfile = str(cert_path)

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
    )
