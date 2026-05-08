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
selected_point = None
STEP = 5

def mm_to_canvas(x, y):
    cx = CANVAS//2 + int(x * SCALE)
    cy = CANVAS//2 - int(y * SCALE)
    return (cx, cy)

def canvas_to_mm(cx, cy):
    x = (cx - CANVAS//2) / SCALE
    y = -(cy - CANVAS//2) / SCALE
    return (x, y)

def on_click(event, cx, cy, flags, param):
    global selected_point
    if event != cv2.EVENT_LBUTTONDOWN:
        return
    if len(physical_points) < 4:
        x_mm, y_mm = canvas_to_mm(cx, cy)
        idx = len(physical_points)
        physical_points.append([x_mm, y_mm])
        screen_points.append(SCREEN_CORNERS[idx])
        selected_point = idx
        print(f"[CAL] Punto {idx+1}/4 — ({x_mm:.1f}mm, {y_mm:.1f}mm) → pantalla {SCREEN_CORNERS[idx]}")
        print(f"[CAL] Ajusta con flechas ↑↓←→, confirma con ENTER")
    else:
        for i, (x_mm, y_mm) in enumerate(physical_points):
            px, py = mm_to_canvas(x_mm, y_mm)
            if abs(cx - px) < 15 and abs(cy - py) < 15:
                selected_point = i
                print(f"[CAL] Editando punto {i+1}")
                break

def draw(scan_points, phys_pts):
    canvas = np.zeros((CANVAS, CANVAS, 3), dtype=np.uint8)

    for mm in range(-3000, 3001, 500):
        px, _ = mm_to_canvas(mm, 0)
        _, py = mm_to_canvas(0, mm)
        cv2.line(canvas, (px, 0), (px, CANVAS), (30, 30, 30), 1)
        cv2.line(canvas, (0, py), (CANVAS, py), (30, 30, 30), 1)
        if 0 <= px < CANVAS:
            cv2.putText(canvas, f"{mm//10}cm", (px+2, CANVAS-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (50, 50, 50), 1)

    for x, y in scan_points:
        px, py = mm_to_canvas(x, y)
        if 0 <= px < CANVAS and 0 <= py < CANVAS:
            cv2.circle(canvas, (px, py), 2, (0,255,0), -1)

    cv2.circle(canvas, (CANVAS//2, CANVAS//2), 6, (255,0,0), -1)

    for i, (x_mm, y_mm) in enumerate(phys_pts):
        px, py = mm_to_canvas(x_mm, y_mm)
        color = (0, 255, 255) if i == selected_point else (0, 100, 255)
        cv2.circle(canvas, (px, py), 10, color, -1)
        cv2.circle(canvas, (px, py), 14, color, 2)
        cv2.putText(canvas, str(i+1), (px+12, py-8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(canvas, f"({x_mm:.0f},{y_mm:.0f})mm",
                   (px+12, py+10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

    n = len(phys_pts)
    if selected_point is not None and n > 0:
        msg = f"Editando P{selected_point+1} — flechas para ajustar — ENTER para confirmar"
    elif n < 4:
        msg = f"Clic {n+1}/4: {CORNERS[n]}"
    else:
        msg = "4 puntos listos! [S] guardar  [R] reiniciar  [Q] salir"

    cv2.rectangle(canvas, (0, 0), (CANVAS, 30), (20,20,20), -1)
    cv2.putText(canvas, msg, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1)
    cv2.putText(canvas, "[Q] Salir  [R] Reiniciar  [S] Guardar  Flechas: ajustar punto seleccionado",
               (5, CANVAS-5), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (130,130,130), 1)

    return canvas

def main():
    global selected_point

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
            key = cv2.waitKeyEx(30) & 0xFFFFFF

            if key == ord("q"):
                break
            elif key == ord("r"):
                physical_points.clear()
                screen_points.clear()
                selected_point = None
                print("[CAL] Reiniciado")
            elif key == ord("s"):
                if len(physical_points) == 4:
                    matrix = compute_homography(physical_points, screen_points)
                    np.save(str(CALIBRATION_FILE), matrix)
                    print(f"[CAL] ✅ Matriz guardada en {CALIBRATION_FILE}")
                    break
                else:
                    print("[CAL] Necesitas 4 puntos primero")
            elif key == 13:  # ENTER
                if selected_point is not None:
                    x_mm, y_mm = physical_points[selected_point]
                    print(f"[CAL] Punto {selected_point+1} confirmado: ({x_mm:.1f}mm, {y_mm:.1f}mm)")
                    selected_point = None

            if selected_point is not None and len(physical_points) > selected_point:
                x_mm, y_mm = physical_points[selected_point]
                cx, cy = mm_to_canvas(x_mm, y_mm)
                moved = False

                if key == 2490368:    # ↑
                    cy -= STEP
                    moved = True
                elif key == 2621440:  # ↓
                    cy += STEP
                    moved = True
                elif key == 2424832:  # ←
                    cx -= STEP
                    moved = True
                elif key == 2555904:  # →
                    cx += STEP
                    moved = True

                if moved:
                    new_x, new_y = canvas_to_mm(cx, cy)
                    physical_points[selected_point] = [new_x, new_y]

    except KeyboardInterrupt:
        pass
    finally:
        handler.disconnect()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()