# utils/logger.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan
# Descripción: Sistema de logs centralizado. Todos los archivos
#              del proyecto importan el logger desde acá.
#              Farly puede revisar los logs en la carpeta logs/
#              cuando algo falle en el parque.

import sys
from loguru import logger
from sistema_camara.config.settings import LOG_NIVEL

# ─────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────

# Eliminar el logger por defecto de loguru
logger.remove()

# Logger en consola — Farly lo ve en tiempo real mientras el sistema corre
logger.add(
    sys.stdout,
    level=LOG_NIVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan> | "
           "<level>{message}</level>",
    colorize=True
)

# Logger en archivo — queda guardado para revisar después si algo falló
logger.add(
    "logs/parketr3s_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}",
    rotation="1 day",       # Crea un archivo nuevo cada día
    retention="7 days",     # Guarda solo los últimos 7 días
    encoding="utf-8"
)

# ─────────────────────────────────────────
# MENSAJES ESTÁNDAR DEL SISTEMA
# ─────────────────────────────────────────
# Estos son atajos para los mensajes más comunes.
# Jean los importa y los usa así:
#   from sistema_camara.utils.logger import log_camara_conectada
#   log_camara_conectada(0)

def log_camara_conectada(indice: int):
    logger.info(f"✅ Cámara conectada en índice {indice}")

def log_camara_error(indice: int):
    logger.error(f"❌ No se encontró la cámara en índice {indice}")

def log_mediapipe_listo():
    logger.info("✅ MediaPipe inicializado correctamente")

def log_jugador_detectado():
    logger.info("🧍 Jugador detectado en cámara")

def log_jugador_perdido():
    logger.warning("⚠️ Jugador perdido — confianza por debajo del umbral")

def log_websocket_listo(puerto: int):
    logger.info(f"✅ Servidor WebSocket escuchando en puerto {puerto}")

def log_websocket_cliente_conectado():
    logger.info("🎮 Frontend conectado al WebSocket")

def log_websocket_cliente_desconectado():
    logger.warning("⚠️ Frontend desconectado del WebSocket")

def log_fps(fps: float):
    logger.debug(f"📊 FPS actual: {fps:.1f}")