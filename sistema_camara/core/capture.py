import cv2
import threading
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
    log_jugador_perdido,
    logger
)

RUTA_MODELO = "pose_landmarker.task"
MAX_JUGADORES = 2


class CapturaCamara:
    def __init__(self):
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

        self._filtros             = [FiltroEsqueleto() for _ in range(MAX_JUGADORES)]
        self._camara              = None
        self._jugadores_visibles  = 0
        self._timestamp_ms        = 0

        # ── Hilo de lectura en background ──
        self._frame_actual = None
        self._frame_lock   = threading.Lock()
        self._hilo_lectura = None
        self._corriendo    = False

    def conectar(self) -> bool:
        self._camara = cv2.VideoCapture(CAMARA_INDEX, cv2.CAP_MSMF)

        if not self._camara.isOpened():
            log_camara_error(CAMARA_INDEX)
            return False

        self._camara.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMARA_ANCHO)
        self._camara.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMARA_ALTO)
        self._camara.set(cv2.CAP_PROP_FPS,          CAMARA_FPS)
        self._camara.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self._camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        log_camara_conectada(CAMARA_INDEX)

        # Iniciar hilo de lectura continua
        self._corriendo    = True
        self._hilo_lectura = threading.Thread(target=self._leer_continuo, daemon=True)
        self._hilo_lectura.start()

        return True

    def _leer_continuo(self):
        """
        Hilo en background que lee frames a máxima velocidad
        y guarda solo el más reciente. Así MediaPipe siempre
        procesa el frame actual, no uno de hace 2 segundos.
        """
        while self._corriendo:
            if not self._camara or not self._camara.isOpened():
                break
            ok, frame = self._camara.read()
            if ok:
                with self._frame_lock:
                    self._frame_actual = frame

    def desconectar(self):
        self._corriendo = False
        if self._hilo_lectura:
            self._hilo_lectura.join(timeout=1)
        if self._camara:
            self._camara.release()
        self._pose.close()
        logger.info("🔌 Cámara desconectada correctamente")

    def leer_frame(self) -> dict | None:
        # Tomar el frame más reciente del hilo
        with self._frame_lock:
            if self._frame_actual is None:
                return None
            frame = self._frame_actual.copy()

        # ── Convertir a formato MediaPipe ──
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image  = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )

        self._timestamp_ms += 1
        resultado = self._pose.detect_for_video(mp_image, self._timestamp_ms)

        cantidad = len(resultado.pose_landmarks) if resultado.pose_landmarks else 0

        if cantidad != self._jugadores_visibles:
            if cantidad == 0:
                log_jugador_perdido()
            else:
                logger.info(f"👤 Jugadores detectados: {cantidad}")
            self._jugadores_visibles = cantidad

        if cantidad == 0:
            return {
                "jugadores_detectados": 0,
                "landmarks":            []
            }

        poses_ordenadas = sorted(
            resultado.pose_landmarks,
            key=lambda lm: lm[0].x
        )

        landmarks_todos = []
        for i, pose in enumerate(poses_ordenadas):
            landmarks_todos.append(self._filtros[i].aplicar(pose))

        return {
            "jugadores_detectados": cantidad,
            "landmarks":            landmarks_todos
        }