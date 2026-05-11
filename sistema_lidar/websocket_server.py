import asyncio
import time
import logging
import orjson
import websockets
from websockets.server import WebSocketServerProtocol
from config.settings import WS_HOST, WS_PORT

import sys
sys.path.append("sistema_lidar")

logger = logging.getLogger(__name__)


class WebSocketServer:
    def __init__(self) -> None:
        self.clients: set[WebSocketServerProtocol] = set()
        self.on_mode_change = None

    async def _handle(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        print(f"[WS] Cliente conectado: {ws.remote_address} | Total: {len(self.clients)}")
        try:
            async for message in ws:
                try:
                    data = orjson.loads(message)
                    if data.get("event") == "set_mode":
                        mode = data.get("mode")
                        if self.on_mode_change and mode in ("pizarra", "penaltis"):
                            self.on_mode_change(mode)
                except Exception:
                    pass
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            self.clients.discard(ws)
            print(f"[WS] Cliente desconectado | Total: {len(self.clients)}")

    async def broadcast_touches(self, touches: list) -> None:
        if not self.clients:
            return
        payload = orjson.dumps({
            "event": "hit",
            "touches": touches,
            "timestamp": int(time.time())
        }).decode("utf-8")
        dead = set()
        for client in self.clients:
            try:
                await client.send(payload)
            except Exception:
                dead.add(client)
        self.clients -= dead

    async def start(self) -> None:
        print(f"[WS] Servidor iniciado en ws://{WS_HOST}:{WS_PORT}")
        async with websockets.serve(self._handle, WS_HOST, WS_PORT):
            await asyncio.Future()