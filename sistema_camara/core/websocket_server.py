# sistema_camara/core/websocket_server.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Jean
# Descripción: Servidor WebSocket asíncrono para el sistema de cámara.

import asyncio
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sistema_camara.config.settings import WS_HOST, WS_PUERTO_CAMARA
from sistema_camara.utils.logger import (
    log_websocket_listo, 
    log_websocket_cliente_conectado, 
    log_websocket_cliente_desconectado
)

app = FastAPI()

class CameraWebSocketServer:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        log_websocket_cliente_conectado()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        log_websocket_cliente_desconectado()

    async def broadcast(self, data: dict):
        """Envía el JSON a todos los clientes (Frontend) conectados."""
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                # Si falla el envío a un cliente, se ignora para no bloquear el loop
                pass

manager = CameraWebSocketServer()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantiene la conexión viva. El envío real se hace vía broadcast.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def run_server():
    import uvicorn
    log_websocket_listo(WS_PUERTO_CAMARA)
    uvicorn.run(app, host=WS_HOST, port=WS_PUERTO_CAMARA, log_level="warning")