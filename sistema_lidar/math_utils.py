import math
import numpy as np
import cv2
from typing import Optional, Tuple
from numpy.typing import NDArray


def polar_to_cartesian(angle_deg: float, distance_mm: float) -> Tuple[float, float]:
    angle_rad = math.radians(angle_deg)
    x = distance_mm * math.cos(angle_rad)
    y = distance_mm * math.sin(angle_rad)
    return (x, y)


def apply_homography(
    point_mm: Tuple[float, float],
    matrix: NDArray
) -> Optional[Tuple[int, int]]:
    src = np.array([[[point_mm[0], point_mm[1]]]], dtype=np.float64)
    try:
        dst = cv2.perspectiveTransform(src, matrix)
        x = float(dst[0][0][0])
        y = float(dst[0][0][1])
        if not (math.isfinite(x) and math.isfinite(y)):
            return None
        return (round(x), round(y))
    except cv2.error:
        return None


def compute_homography(
    physical_points: list,
    screen_points: list
) -> NDArray:
    src = np.array(physical_points, dtype=np.float32)
    dst = np.array(screen_points, dtype=np.float32)
    matrix, _ = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    if matrix is None:
        raise ValueError("No se pudo calcular la homografía.")
    return matrix