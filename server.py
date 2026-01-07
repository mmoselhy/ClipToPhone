import asyncio
import json
import time
from fastapi import FastAPI, WebSocket
from pairing import ensure_config

app = FastAPI()
clients = set()
config = ensure_config()
token = config['token']

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    authenticated = False
    try:
        # Wait for hello message within 5 seconds
        data = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)
        if data.get("type") == "hello" and data.get("token") == token:
            authenticated = True
            clients.add(websocket)
        else:
            await websocket.close(code=1008)  # Policy violation
            return

        # Keep the connection alive
        while True:
            await asyncio.sleep(30)  # Ping or just keep alive

    except asyncio.TimeoutError:
        await websocket.close(code=1008)
    except Exception:
        pass
    finally:
        if authenticated:
            clients.discard(websocket)

async def broadcast_clipboard(content: str):
    message = {
        "type": "clipboard",
        "contentType": "text",
        "content": content,
        "ts": int(time.time())
    }
    json_message = json.dumps(message)
    disconnected = []
    for client in clients.copy():
        try:
            await client.send_text(json_message)
        except Exception:
            disconnected.append(client)
    for client in disconnected:
        clients.discard(client)