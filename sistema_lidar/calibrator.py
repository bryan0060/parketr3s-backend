import sys
import cv2
import numpy as np
sys.path.append("sistema_lidar")

from lidar_handler import LidarHandler
from math_utils import polar_to_cartesian, compute_homography
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, CALIBRATION_FILE

CANVAS = 800
SCALE = 0.10
CORNERS = ["Superior-Izquierda", "Superior-Derecha", "Inferior-Derecha", "Inferior-Izquierda"]
SCREEN_CORNERS = [(0,0), (SCREEN_WIDTH-1, 0), (SCREEN_WIDTH-1, SCREEN_HEIGHT-1), (0, SCREEN_HEIGHT-1)]

physical_points = []
screen_points = []
last_scan = []

def mm_to_canvas(x, y):
    cx = CANVAS//2 + int(x * SCALE)
    cy = CANVAS//2 - int(y * SCALE)
    return (cx, cy)

def canvas_to_mm(cx, cy):
    x = (cx - CANVAS//2) / SCALE
    y = -(cy - CANVAS//2) / SCALE
    return (x, y)

def on_click(event, cx, cy, flags, param):
    if event != cv2.EVENT_LBUTTONDOWN:
        return
    if len(physical_points) >= 4:
        return
    x_mm, y_mm = canvas_to_mm(cx, cy)
    idx = len(physical_points)
    physical_points.append((x_mm, y_mm))
    screen_points.append(SCREEN_CORNERS[idx])
    print(f"[CAL] Punto {idx+1}/4 — ({x_mm:.1f}mm, {y_mm:.1f}mm) → pantalla {SCREEN_CORNERS[idx]}")

def draw(scan_points, phys_pts):
    canvas = np.zeros((CANVAS, CANVAS, 3), dtype=np.uint8)
    for x, y in scan_points:
        px, py = mm_to_canvas(x, y)
        if 0 <= px < CANVAS and 0 <= py < CANVAS:
            cv2.circle(canvas, (px, py), 2, (0,255,0), -1)
    cx, cy = CANVAS//2, CANVAS//2
    cv2.circle(canvas, (cx, cy), 6, (255,0,0), -1)
    for i, (x, y) in enumerate(phys_pts):
        px, py = mm_to_canvas(x, y)
        cv2.circle(canvas, (px, py), 8, (0,100,255), -1)
        cv2.putText(canvas, str(i+1), (px+10, py-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,100,255), 2)
    n = len(phys_pts)
    if n < 4:
        msg = f"Clic {n+1}/4: {CORNERS[n]}"
    else:
        msg = "Listo! [S] guardar  [R] reiniciar  [Q] salir"
    cv2.putText(canvas, msg, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1)
    return canvas

def main():
    handler = LidarHandler()
    handler.connect()
    if not handler.connected:
        print("❌ No se pudo conectar al sensor")
        return

    cv2.namedWindow("Calibrador")
    cv2.setMouseCallback("Calibrador", on_click)

    import threading

    def lidar_thread():
        for angle, distance in handler.read_loop():
            x, y = polar_to_cartesian(angle, distance)
            last_scan.append((x, y))
            if len(last_scan) > 500:
                last_scan.pop(0)

    t = threading.Thread(target=lidar_thread, daemon=True)
    t.start()

    try:
        while True:
            canvas = draw(last_scan, physical_points)
            cv2.imshow("Calibrador", canvas)
            key = cv2.waitKey(30) & 0xFF

            if key == ord("q"):
                break
            elif key == ord("r"):
                physical_points.clear()
                screen_points.clear()
                print("[CAL] Reiniciado")
            elif key == ord("s"):
                if len(physical_points) == 4:
                    matrix = compute_homography(physical_points, screen_points)
                    np.save(str(CALIBRATION_FILE), matrix)
                    print(f"[CAL] ✅ Matriz guardada en {CALIBRATION_FILE}")
                    break
                else:
                    print("[CAL] Necesitas 4 puntos primero")
    except KeyboardInterrupt:
        pass
    finally:
        handler.disconnect()
        cv2.destroyAllWindows()
        
    handler = LidarHandler()
    handler.connect()
    if not handler.connected:
        print("❌ No se pudo conectar al sensor")
        return

    cv2.namedWindow("Calibrador")
    cv2.setMouseCallback("Calibrador", on_click)

    try:
        for angle, distance in handler.read_loop():
            x, y = polar_to_cartesian(angle, distance)
            last_scan.append((x, y))
            if len(last_scan) > 500:
                last_scan.pop(0)

            canvas = draw(last_scan, physical_points)
            cv2.imshow("Calibrador", canvas)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            elif key == ord("r"):
                physical_points.clear()
                screen_points.clear()
                print("[CAL] Reiniciado")
            elif key == ord("s"):
                if len(physical_points) == 4:
                    matrix = compute_homography(physical_points, screen_points)
                    np.save(str(CALIBRATION_FILE), matrix)
                    print(f"[CAL] ✅ Matriz guardada en {CALIBRATION_FILE}")
                    break
                else:
                    print("[CAL] Necesitas 4 puntos primero")
    except KeyboardInterrupt:
        pass
    finally:
        handler.disconnect()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()