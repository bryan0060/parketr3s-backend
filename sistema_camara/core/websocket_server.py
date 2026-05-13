# sistema_camara/core/websocket_server.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Jean / Bryan
# Descripción: Servidor WebSocket asíncrono para el sistema de cámara.
#              Recibe el juego activo y el modo (solo/duo) desde el Frontend
#              y notifica al bucle principal para cambiar de processor.

import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sistema_camara.utils.logger import (
    log_websocket_listo,
    log_websocket_cliente_conectado,
    log_websocket_cliente_desconectado,
    logger
)

app = FastAPI()


class CameraWebSocketServer:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

        # ── Juego activo ──
        # Empieza en None — el frontend debe mandar el juego al conectarse.
        # main.py lee esta variable en cada frame para saber qué processor usar.
        self.juego_activo: str | None = None

        # ── Modo de juego ──
        # "solo" = 1 jugador (default), "duo" = 2 jugadores cooperativos
        self.modo: str = "solo"

        # Juegos y modos válidos
        self._juegos_validos = {"ritmo", "esquive", "impacto", "poses"}
        self._modos_validos  = {"solo", "duo"}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        log_websocket_cliente_conectado()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        log_websocket_cliente_desconectado()

    async def broadcast(self, data: dict):
        """Envía el JSON a todos los clientes conectados."""
        conexiones_muertas = []

        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                conexiones_muertas.append(connection)

        for conexion in conexiones_muertas:
            if conexion in self.active_connections:
                self.active_connections.remove(conexion)

    def cambiar_juego(self, juego: str):
        """Cambia el juego activo si el nombre es válido."""
        if juego in self._juegos_validos:
            self.juego_activo = juego
            logger.info(f"🎮 Juego activo cambiado a: {juego}")
        else:
            logger.warning(f"⚠️ El frontend mandó un juego desconocido: {juego}")

    def cambiar_modo(self, modo: str):
        """Cambia el modo de juego si es válido."""
        if modo in self._modos_validos:
            self.modo = modo
            logger.info(f"👥 Modo cambiado a: {modo}")
        else:
            logger.warning(f"⚠️ Modo desconocido: {modo}")


manager = CameraWebSocketServer()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            mensaje_raw = await websocket.receive_text()

            try:
                mensaje = json.loads(mensaje_raw)

                # El frontend manda: { "juego": "poses", "modo": "duo" }
                if "juego" in mensaje:
                    manager.cambiar_juego(mensaje["juego"])

                if "modo" in mensaje:
                    manager.cambiar_modo(mensaje["modo"])

            except json.JSONDecodeError:
                logger.warning(f"⚠️ Mensaje no válido recibido: {mensaje_raw}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)