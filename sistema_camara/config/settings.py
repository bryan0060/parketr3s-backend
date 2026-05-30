# config/settings.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan
# Descripción: Panel de control del sistema. Todos los valores
#              configurables viven aquí. Nadie más escribe números
#              directamente en su código — los importan desde acá.

from dotenv import load_dotenv
import os

# Carga las variables del archivo .env
load_dotenv()

# ─────────────────────────────────────────
# CÁMARA
# ─────────────────────────────────────────

# Cuál cámara usar. 0 es la primera que detecta Windows.
# Si hay varias conectadas, Farly cambia este número en el .env
CAMARA_INDEX = int(os.getenv("CAMARA_INDEX", 0))

CAMARA_ANCHO = int(os.getenv("CAMARA_RESOLUCION_ANCHO", 1920))
CAMARA_ALTO  = int(os.getenv("CAMARA_RESOLUCION_ALTO", 1080))
CAMARA_FPS   = int(os.getenv("CAMARA_FPS_OBJETIVO", 30))

# ─────────────────────────────────────────
# MEDIAPIPE
# ─────────────────────────────────────────

# Qué tan complejo es el modelo de detección.
# 0 = rápido pero menos preciso
# 1 = equilibrado (recomendado)
# 2 = más preciso pero más lento
MP_COMPLEJIDAD = int(os.getenv("MEDIAPIPE_MODEL_COMPLEXITY", 1))

# Qué tan seguro tiene que estar MediaPipe para decir
# "sí, ahí hay una persona". 0.0 a 1.0
MP_CONFIANZA_DETECCION = float(os.getenv("MEDIAPIPE_MIN_DETECTION_CONF", 0.7))

# Qué tan seguro para seguir rastreando a alguien que ya detectó
MP_CONFIANZA_TRACKING  = float(os.getenv("MEDIAPIPE_MIN_TRACKING_CONF", 0.5))

# ─────────────────────────────────────────
# ONE EURO FILTER (Bryan)
# ─────────────────────────────────────────

# Frecuencia base del filtro. Debe coincidir con los FPS de la cámara.
ONE_EURO_FREQ     = float(os.getenv("CAMARA_FPS_OBJETIVO", 60))

# Qué tanto suavizar cuando el movimiento es lento.
# Número más bajo = más suavizado = menos temblor pero más retraso
ONE_EURO_MINCUTOFF = float(os.getenv("ONE_EURO_MINCUTOFF", 1.0))

# Qué tanto reducir el suavizado cuando el movimiento es rápido.
# Número más alto = menos suavizado en movimientos rápidos = menos lag
ONE_EURO_BETA      = float(os.getenv("ONE_EURO_BETA", 0.007))

# Suavizado interno de la velocidad del filtro. Generalmente no se toca.
ONE_EURO_DCUTOFF   = float(os.getenv("ONE_EURO_DCUTOFF", 1.0))

# ─────────────────────────────────────────
# WEBSOCKET
# ─────────────────────────────────────────

WS_HOST          = "localhost"
WS_PUERTO_CAMARA = int(os.getenv("CAMARA_PUERTO_WS", 8080))

# ─────────────────────────────────────────
# JUEGO — ESQUIVE
# ─────────────────────────────────────────

# Límite izquierdo de la zona central del frame (0.0 a 1.0)

ESQUIVE_DESPLAZAMIENTO = float(os.getenv("ESQUIVE_DESPLAZAMIENTO", "0.08"))

# Si hip_x < este valor → LEFT
ESQUIVE_ZONA_IZQUIERDA      = float(os.getenv("ESQUIVE_ZONA_IZQUIERDA",      0.38))

# Límite derecho de la zona central del frame (0.0 a 1.0)
# Si hip_x > este valor → RIGHT
ESQUIVE_ZONA_DERECHA        = float(os.getenv("ESQUIVE_ZONA_DERECHA",        0.62))

# Cuántos "alturas de torso" deben bajar las caderas para agacharse.
ESQUIVE_UMBRAL_AGACHARSE    = float(os.getenv("ESQUIVE_UMBRAL_AGACHARSE",    0.25))

# Frames consecutivos para confirmar un cambio de carril.
ESQUIVE_FRAMES_CONFIRMACION = int(os.getenv("ESQUIVE_FRAMES_CONFIRMACION",   3))

# ─────────────────────────────────────────
# JUEGO — IMPACTO
# ─────────────────────────────────────────

# Velocidad mínima para considerar que fue un golpe.
# Este número se ajusta en las pruebas físicas en el parque.
IMPACTO_UMBRAL_VELOCIDAD    = 8.0

# Aceleración mínima para confirmar el golpe.
IMPACTO_UMBRAL_ACELERACION  = 50.0

# ─────────────────────────────────────────
# LOGS
# ─────────────────────────────────────────

LOG_NIVEL = os.getenv("LOG_NIVEL", "INFO")