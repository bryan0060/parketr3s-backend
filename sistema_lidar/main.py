import asyncio
import threading
import sys
sys.path.append("sistema_lidar")

from lidar_handler import LidarHandler
from processor import Processor
from websocket_server import WebSocketServer

handler = LidarHandler()

MAX_TOUCHES = 4
MATCH_DIST = 150  # px para considerar mismo toque


def assign_ids(prev_touches: dict, new_points: list) -> dict:
    """
    Asigna IDs estables a los nuevos puntos basándose en proximidad
    con los puntos anteriores.
    """
    assigned = {}
    available_ids = list(range(MAX_TOUCHES))
    used_prev = set()

    # Emparejar nuevos puntos con IDs anteriores por proximidad
    for x, y in new_points:
        best_id = None
        best_dist = MATCH_DIST

        for tid, (px, py) in prev_touches.items():
            if tid in used_prev:
                continue
            dist = ((x - px)**2 + (y - py)**2)**0.5
            if dist < best_dist:
                best_dist = dist
                best_id = tid

        if best_id is not None:
            assigned[best_id] = (x, y)
            used_prev.add(best_id)
        else:
            # Nuevo toque — asignar ID libre
            for tid in available_ids:
                if tid not in assigned and tid not in prev_touches:
                    assigned[tid] = (x, y)
                    break

    return assigned


async def main():
    processor = Processor()
    server = WebSocketServer()
    loop = asyncio.get_running_loop()

    def lidar_thread():
        from collections import deque
        import time

        # History por touch ID
        histories = {i: deque(maxlen=6) for i in range(MAX_TOUCHES)}
        prev_touches = {}
        last_point_time = time.monotonic()
        LIFT_THRESHOLD = 0.12

        for angle, distance in handler.read_loop():
            points = processor.process(angle, distance)
            now = time.monotonic()

            if not points:
                if now - last_point_time > LIFT_THRESHOLD:
                    prev_touches.clear()
                    for h in histories.values():
                        h.clear()
                continue

            last_point_time = now

            # Asignar IDs estables
            current_touches = assign_ids(prev_touches, points)
            prev_touches = current_touches

            touches_payload = []
            for tid, (x, y) in current_touches.items():
                h = histories[tid]

                if h:
                    last = h[-1]
                    speed = ((x - last[0])**2 + (y - last[1])**2)**0.5
                else:
                    speed = 0

                # Limpiar history de IDs que no están activos
                if tid not in current_touches:
                    h.clear()

                h.append((x, y))

                n = min(2, len(h)) if speed > 80 else len(h)
                recent = list(h)[-n:]
                avg_x = int(sum(p[0] for p in recent) / len(recent))
                avg_y = int(sum(p[1] for p in recent) / len(recent))

                touches_payload.append({"id": tid, "x": avg_x, "y": avg_y})

            asyncio.run_coroutine_threadsafe(
                server.broadcast_touches(touches_payload), loop
            )

    t = threading.Thread(target=lidar_thread, daemon=True)
    t.start()
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[MAIN] Apagando sistema...")
    finally:
        handler.disconnect()
        print("[MAIN] Motor detenido. Sistema apagado limpiamente.")