import numpy as np
import sys
sys.path.append("sistema_lidar")

from math_utils import polar_to_cartesian, apply_homography
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, CALIBRATION_FILE


class Processor:
    def __init__(self) -> None:
        self.matrix = None
        self._load_matrix()

    def _load_matrix(self) -> None:
        if not CALIBRATION_FILE.exists():
            raise FileNotFoundError(
                f"No se encontró la matriz de calibración en {CALIBRATION_FILE}\n"
                "Ejecuta primero: python sistema_lidar/calibrator.py"
            )
        self.matrix = np.load(str(CALIBRATION_FILE))
        print(f"[PROC] Matriz de homografía cargada")

    def process(self, angle: float, distance: float):
        x_mm, y_mm = polar_to_cartesian(angle, distance)
        point = apply_homography((x_mm, y_mm), self.matrix)
        if point is None:
            return None
        x_px, y_px = point
        if 0 <= x_px < SCREEN_WIDTH and 0 <= y_px < SCREEN_HEIGHT:
            return (x_px, y_px)
        return None