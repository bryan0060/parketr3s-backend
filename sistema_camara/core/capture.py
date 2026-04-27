# core/capture.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan (temporalmente)
# Descripción: Captura de cámara con OpenCV + MediaPipe Pose Landmarker.
#              Usa la nueva API de MediaPipe Tasks (v0.10+)
#              Lee frame por frame, detecta el cuerpo del jugador
#              y devuelve los landmarks filtrados listos para
#              los processors.

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

class CapturaCamara:
    def __init__(self):
        # ── Inicializar MediaPipe Pose Landmarker ──
        opciones = mp_vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=RUTA_MODELO
            ),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=MP_CONFIANZA_DETECCION,
            min_pose_presence_confidence=MP_CONFIANZA_DETECCION,
            min_tracking_confidence=MP_CONFIANZA_TRACKING
        )
        self._pose = mp_vision.PoseLandmarker.create_from_options(opciones)
        log_mediapipe_listo()

        # ── Inicializar el filtro del esqueleto ──
        self._filtro = FiltroEsqueleto()

        # ── Estado interno ──
        self._camara          = None
        self._jugador_visible = False
        self._timestamp_ms    = 0  # MediaPipe Tasks requiere timestamp incremental

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
        y devuelve los landmarks filtrados.
        """
        if not self._camara or not self._camara.isOpened():
            logger.error("❌ Se intentó leer un frame sin cámara conectada")
            return None

        ok, frame = self._camara.read()

        if not ok:
            logger.warning("⚠️ No se pudo leer el frame de la cámara")
            return None

        # ── Convertir a formato MediaPipe ──
        frame_rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image     = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )

        # ── Incrementar timestamp ──
        # MediaPipe Tasks requiere que el timestamp sea siempre creciente
        self._timestamp_ms += 1

        # ── Procesar con MediaPipe ──
        resultado = self._pose.detect_for_video(mp_image, self._timestamp_ms)

        # ── Sin jugador detectado ──
        if not resultado.pose_landmarks or len(resultado.pose_landmarks) == 0:
            if self._jugador_visible:
                log_jugador_perdido()
                self._jugador_visible = False

            return {
                "jugador_detectado": False,
                "landmarks":         None
            }

        # ── Jugador detectado ──
        if not self._jugador_visible:
            log_jugador_detectado()
            self._jugador_visible = True

        # Aplicar filtro al esqueleto completo
        landmarks_filtrados = self._filtro.aplicar(
            resultado.pose_landmarks[0]
        )

        return {
            "jugador_detectado": True,
            "landmarks":         landmarks_filtrados
        }