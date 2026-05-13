# sistema_camara/core/capture.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan (temporalmente)
# Descripción: Captura de cámara con OpenCV + MediaPipe Pose Landmarker.
#              Usa la nueva API de MediaPipe Tasks (v0.10+)
#              Detecta hasta 2 jugadores simultáneamente.
#              Los esqueletos se ordenan por posición X (izquierda→derecha)
#              para que jugador_1 siempre sea el de la izquierda.

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

from sistema_camara.config.settings import (
    CAMARA_INDEX,
    CAMARA_ANCHO,
    CAMARA_ALTO,
    CAMARA_FPS,
    MP_COMPLEJIDAD,
    MP_CONFIANZA_DETECCION,
    MP_CONFIANZA_TRACKING
)
from sistema_camara.core.filters import FiltroEsqueleto
from sistema_camara.utils.logger import (
    log_camara_conectada,
    log_camara_error,
    log_mediapipe_listo,
    log_jugador_detectado,
    log_jugador_perdido,
    logger
)

# Ruta al modelo descargado
RUTA_MODELO = "pose_landmarker.task"

# Máximo de jugadores soportados
MAX_JUGADORES = 2


class CapturaCamara:
    def __init__(self):
        # ── Inicializar MediaPipe Pose Landmarker ──
        opciones = mp_vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=RUTA_MODELO
            ),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_poses=MAX_JUGADORES,
            min_pose_detection_confidence=MP_CONFIANZA_DETECCION,
            min_pose_presence_confidence=MP_CONFIANZA_DETECCION,
            min_tracking_confidence=MP_CONFIANZA_TRACKING
        )
        self._pose = mp_vision.PoseLandmarker.create_from_options(opciones)
        log_mediapipe_listo()

        # ── Un filtro independiente por cada jugador ──
        # Cada FiltroEsqueleto mantiene su propio estado interno
        # para que el suavizado sea consistente por jugador.
        self._filtros = [FiltroEsqueleto() for _ in range(MAX_JUGADORES)]

        # ── Estado interno ──
        self._camara              = None
        self._jugadores_visibles  = 0
        self._timestamp_ms        = 0

    # ─────────────────────────────────────────
    # CONEXIÓN CON LA CÁMARA
    # ─────────────────────────────────────────

    def conectar(self) -> bool:
        """
        Abre la cámara y configura resolución y FPS.
        Devuelve True si se conectó correctamente, False si falló.
        """
        self._camara = cv2.VideoCapture(CAMARA_INDEX)

        if not self._camara.isOpened():
            log_camara_error(CAMARA_INDEX)
            return False

        self._camara.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMARA_ANCHO)
        self._camara.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMARA_ALTO)
        self._camara.set(cv2.CAP_PROP_FPS,          CAMARA_FPS)

        log_camara_conectada(CAMARA_INDEX)
        return True

    def desconectar(self):
        """
        Cierra la cámara y libera los recursos de MediaPipe.
        """
        if self._camara:
            self._camara.release()
        self._pose.close()
        logger.info("🔌 Cámara desconectada correctamente")

    # ─────────────────────────────────────────
    # LECTURA DE FRAMES
    # ─────────────────────────────────────────

    def leer_frame(self) -> dict | None:
        """
        Lee un frame de la cámara, lo procesa con MediaPipe
        y devuelve los landmarks filtrados de todos los jugadores detectados.

        Retorna:
            {
                "jugadores_detectados": int,    # 0, 1 o 2
                "landmarks": [                  # lista de esqueletos
                    [33 dicts],                  # jugador_1 (izquierda)
                    [33 dicts]                   # jugador_2 (derecha)
                ]
            }
        """
        if not self._camara or not self._camara.isOpened():
            logger.error("❌ Se intentó leer un frame sin cámara conectada")
            return None

        ok, frame = self._camara.read()

        if not ok:
            logger.warning("⚠️ No se pudo leer el frame de la cámara")
            return None

        # ── Convertir a formato MediaPipe ──
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image  = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )

        # ── Incrementar timestamp ──
        self._timestamp_ms += 1

        # ── Procesar con MediaPipe ──
        resultado = self._pose.detect_for_video(mp_image, self._timestamp_ms)

        # ── Contar jugadores detectados ──
        cantidad = len(resultado.pose_landmarks) if resultado.pose_landmarks else 0

        # ── Log solo cuando cambia la cantidad ──
        if cantidad != self._jugadores_visibles:
            if cantidad == 0:
                log_jugador_perdido()
            else:
                logger.info(f"👤 Jugadores detectados: {cantidad}")
            self._jugadores_visibles = cantidad

        # ── Sin jugadores ──
        if cantidad == 0:
            return {
                "jugadores_detectados": 0,
                "landmarks":            []
            }

        # ── Ordenar por posición X (izquierda → derecha) ──
        # Esto garantiza que jugador_1 siempre sea el de la izquierda
        # sin importar el orden en que MediaPipe los detecte.
        poses_ordenadas = sorted(
            resultado.pose_landmarks,
            key=lambda lm: lm[0].x  # nariz.x como referencia
        )

        # ── Filtrar cada esqueleto con su filtro independiente ──
        landmarks_todos = []
        for i, pose in enumerate(poses_ordenadas):
            landmarks_todos.append(self._filtros[i].aplicar(pose))

        return {
            "jugadores_detectados": cantidad,
            "landmarks":            landmarks_todos
        }