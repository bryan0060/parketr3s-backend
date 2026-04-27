# sistema_camara/main.py
# Noah Technology Solutions — Parke Tr3s

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

camara = CapturaCamara()
procesador_poses = PosesProcessor()

async def bucle_camara():
    """Bucle infinito que lee la cámara, calcula FPS y emite por WebSocket."""
    if not camara.conectar():
        logger.error("❌ No se pudo iniciar el bucle de cámara. Revisa la conexión.")
        return

    tiempo_anterior = time.time()

    try:
        while True:
            frame = await asyncio.to_thread(camara.leer_frame)
            
            if frame:
                # ── Cálculo de FPS reales ──
                tiempo_actual = time.time()
                diferencia_tiempo = tiempo_actual - tiempo_anterior
                fps_calculados = 1.0 / diferencia_tiempo if diferencia_tiempo > 0 else 0.0
                tiempo_anterior = tiempo_actual

                mensaje = {
                    "timestamp": tiempo_actual,
                    "juego_activo": "poses",
                    "jugador_detectado": frame["jugador_detectado"],
                    "fps_actual": round(fps_calculados, 1)
                }

                if frame["jugador_detectado"] and frame["landmarks"]:
                    datos_poses = procesador_poses.procesar(frame["landmarks"])
                    mensaje["poses"] = datos_poses

                await manager.broadcast(mensaje)
            
            await asyncio.sleep(0.005)
    finally:
        camara.desconectar()

# ── Reemplazo del evento de startup por Lifespan ──
@asynccontextmanager
async def lifespan_context(aplicacion: FastAPI):
    # Código de inicialización (Startup)
    tarea_camara = asyncio.create_task(bucle_camara())
    yield
    # Código de limpieza (Shutdown)
    tarea_camara.cancel()

# Se asigna el lifespan a la instancia de la app ya creada en websocket_server.py
app.router.lifespan_context = lifespan_context

if __name__ == "__main__":
    logger.info("🚀 Iniciando el sistema backend de Parke Tr3s...")
    uvicorn.run(app, host=WS_HOST, port=WS_PUERTO_CAMARA, log_level="warning")