import numpy as np
import sys
sys.path.append("sistema_lidar")

from math_utils import polar_to_cartesian, apply_homography
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, CALIBRATION_FILE

MAX_TOUCHES = 4


def cluster_points(points, max_dist=100.0):
    if not points:
        return []
    clusters = []
    used = [False] * len(points)
    for i, p in enumerate(points):
        if used[i]:
            continue
        group = [p]
        used[i] = True
        for j, q in enumerate(points):
            if used[j]:
                continue
            if ((p[0]-q[0])**2 + (p[1]-q[1])**2)**0.5 < max_dist:
                group.append(q)
                used[j] = True
        closest = min(group, key=lambda p: (p[0]**2 + p[1]**2)**0.5)
        clusters.append(closest)
    return clusters[:MAX_TOUCHES]


class Processor:
    def __init__(self) -> None:
        self.matrix = None
        self._load_matrix()
        self._buffer = []
        self._buffer_size = 10

    def _load_matrix(self) -> None:
        if not CALIBRATION_FILE.exists():
            raise FileNotFoundError(
                f"No se encontró la matriz de calibración en {CALIBRATION_FILE}\n"
                "Ejecuta primero: python sistema_lidar/calibrator.py"
            )
        self.matrix = np.load(str(CALIBRATION_FILE))
        print(f"[PROC] Matriz de homografía cargada")

    def process(self, angle: float, distance: float, mode: str = "pizarra") -> list:
        x_mm, y_mm = polar_to_cartesian(angle, distance)
        self._buffer.append((x_mm, y_mm))

        if len(self._buffer) < self._buffer_size:
            return []

        max_dist = 100.0 if mode == "pizarra" else 300.0
        centroids = cluster_points(self._buffer, max_dist=max_dist)
        self._buffer.clear()

        results = []
        for cx, cy in centroids:
            point = apply_homography((cx, cy), self.matrix)
            if point is None:
                continue
            x_px, y_px = point
            if 0 <= x_px < SCREEN_WIDTH and 0 <= y_px < SCREEN_HEIGHT:
                results.append((x_px, y_px))
        return results