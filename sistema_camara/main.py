# sistema_camara/main.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan
# Descripción: Orquestador principal del sistema de cámara.
#              Lee el juego activo y el modo desde el manager
#              y llama al processor correspondiente en cada frame.

import asyncio
import time
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from sistema_camara.core.capture import CapturaCamara
from sistema_camara.core.processors.poses   import PosesProcessor
from sistema_camara.core.processors.ritmo   import RitmoProcessor
from sistema_camara.core.processors.esquive import EsquiveProcessor
from sistema_camara.core.processors.impacto import ImpactoProcessor
from sistema_camara.core.websocket_server import app, manager
from sistema_camara.config.settings import WS_HOST, WS_PUERTO_CAMARA
from sistema_camara.utils.logger import logger

# ── Instancias de los processors ──
# Se crean una sola vez al arrancar — no en cada frame
procesadores = {
    "poses":   PosesProcessor(),
    "ritmo":   RitmoProcessor(),
    "esquive": EsquiveProcessor(),
    "impacto": ImpactoProcessor(),
}

camara = CapturaCamara()


async def bucle_camara():
    """
    Bucle infinito que:
    1. Lee un frame de la cámara (detecta hasta 2 jugadores)
    2. Revisa qué juego y modo están activos
    3. Llama al processor correspondiente pasándole el modo
    4. Emite el JSON por WebSocket
    """
    if not camara.conectar():
        logger.error("❌ No se pudo iniciar el bucle de cámara.")
        return

    tiempo_anterior    = time.time()
    jugadores_anterior = 0

    try:
        while True:
            frame = await asyncio.to_thread(camara.leer_frame)

            if not frame:
                await asyncio.sleep(0.005)
                continue

            # ── Calcular FPS reales ──
            tiempo_actual     = time.time()
            diferencia_tiempo = tiempo_actual - tiempo_anterior
            fps_calculados    = 1.0 / diferencia_tiempo if diferencia_tiempo > 0 else 0.0
            tiempo_anterior   = tiempo_actual

            # ── Leer estado del manager ──
            juego = manager.juego_activo
            modo  = manager.modo

            # ── Detectar cuando alguien sale del frame ──
            # Solo afecta a Esquive — los demás processors no necesitan reset
            cantidad_actual = frame["jugadores_detectados"]

            if jugadores_anterior > 0 and cantidad_actual == 0:
                if juego == "esquive":
                    procesadores["esquive"].reset()
                    logger.info("🔄 Baseline de Esquive reiniciado — jugador salió del frame")

            jugadores_anterior = cantidad_actual

            # ── Armar mensaje base ──
            mensaje = {
                "timestamp":            tiempo_actual,
                "juego_activo":         juego,
                "modo":                 modo,
                "jugadores_detectados": cantidad_actual,
                "fps_actual":           round(fps_calculados, 1)
            }

            # ── Llamar al processor del juego activo ──
            if juego and cantidad_actual > 0 and frame["landmarks"]:
                procesador = procesadores.get(juego)

                if procesador:
                    mensaje[juego] = procesador.procesar(
                        frame["landmarks"], modo
                    )
                else:
                    logger.warning(f"⚠️ No hay processor para el juego: {juego}")

            # ── Emitir por WebSocket ──
            if manager.active_connections:
                await manager.broadcast(mensaje)

            await asyncio.sleep(0.005)

    finally:
        camara.desconectar()


@asynccontextmanager
async def lifespan_context(aplicacion: FastAPI):
    tarea_camara = asyncio.create_task(bucle_camara())
    yield
    tarea_camara.cancel()


app.router.lifespan_context = lifespan_context

if __name__ == "__main__":
    logger.info("🚀 Iniciando sistema backend Parke Tr3s — Puerto 8080")
    uvicorn.run(app, host=WS_HOST, port=WS_PUERTO_CAMARA, log_level="warning")