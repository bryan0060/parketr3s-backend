# sistema_camara/main.py
# Noah Technology Solutions — Parke Tr3s
# Descripción: Entrypoint principal. Levanta el servidor WebSocket y 
#              ejecuta el bucle de captura de cámara en segundo plano.

import asyncio
import time
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from sistema_camara.core.capture import CapturaCamara
from sistema_camara.core.processors.poses import PosesProcessor
from sistema_camara.core.websocket_server import app, manager
from sistema_camara.config.settings import WS_HOST, WS_PUERTO_CAMARA
from sistema_camara.utils.logger import logger

# Instancias
camara = CapturaCamara()
procesador_poses = PosesProcessor()

async def bucle_camara():
    """Bucle infinito que lee la cámara y envía los datos por WebSocket"""
    if not camara.conectar():
        logger.error("❌ No se pudo iniciar el bucle de cámara. Revisa la conexión.")
        return

    try:
        while True:
            # asyncio.to_thread evita que OpenCV bloquee las conexiones de FastAPI
            frame = await asyncio.to_thread(camara.leer_frame)
            
            if frame:
                # Estructura base del contrato API
                mensaje = {
                    "timestamp": time.time(),
                    "juego_activo": "poses",
                    "jugador_detectado": frame["jugador_detectado"],
                    "fps_actual": 60.0  # TODO: Calcular los FPS reales
                }

                # Si hay jugador, procesamos y adjuntamos los 13 puntos del esqueleto
                if frame["jugador_detectado"] and frame["landmarks"]:
                    datos_poses = procesador_poses.procesar(frame["landmarks"])
                    mensaje["poses"] = datos_poses

                # Transmitir a David y Tomás (si están conectados)
                await manager.broadcast(mensaje)
            
            # Pequeña pausa para no saturar la CPU del Mini PC
            await asyncio.sleep(0.01)
    finally:
        camara.desconectar()

@app.on_event("startup")
async def startup_event():
    # Inicia la cámara justo cuando arranca el servidor web
    asyncio.create_task(bucle_camara())

if __name__ == "__main__":
    logger.info("🚀 Iniciando el sistema backend de Parke Tr3s...")
    uvicorn.run(app, host=WS_HOST, port=WS_PUERTO_CAMARA, log_level="warning")