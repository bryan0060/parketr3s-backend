import asyncio
import threading
import sys
sys.path.append("sistema_lidar")

from lidar_handler import LidarHandler
from processor import Processor
from websocket_server import WebSocketServer

handler = LidarHandler()

MAX_TOUCHES = 4
MATCH_DIST = 200

PROFILES = {
    "pizarra": {
        "buffer_size": 10,
        "smooth_fast": 2,
        "smooth_slow": 3,
        "speed_threshold": 50,
        "lift_threshold": 0.4,
    },
    "penaltis": {
        "buffer_size": 1,
        "smooth_fast": 1,
        "smooth_slow": 1,
        "speed_threshold": 0,
    }
}

current_mode = "pizarra"


def assign_ids(prev_touches: dict, new_points: list) -> dict:
    assigned = {}
    available_ids = list(range(MAX_TOUCHES))
    used_prev = set()

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
            for tid in available_ids:
                if tid not in assigned and tid not in prev_touches:
                    assigned[tid] = (x, y)
                    break

    return assigned


async def main():
    global current_mode

    processor = Processor()
    server = WebSocketServer()
    loop = asyncio.get_running_loop()

    def on_mode_change(mode: str):
        global current_mode
        current_mode = mode
        processor._buffer_size = PROFILES[mode]["buffer_size"]
        processor._buffer.clear()
        print(f"[MAIN] Modo: {mode}")

    server.on_mode_change = on_mode_change

    def lidar_thread():
        from collections import deque
        import time

        histories = {i: deque(maxlen=4) for i in range(MAX_TOUCHES)}
        prev_touches = {}
        last_point_time = time.monotonic()
        LIFT_THRESHOLD = 0.12

        for angle, distance in handler.read_loop():
            profile = PROFILES[current_mode]
            points = processor.process(angle, distance, current_mode)
            now = time.monotonic()

            if not points:
                if now - last_point_time > LIFT_THRESHOLD:
                    prev_touches.clear()
                    for h in histories.values():
                        h.clear()
                continue

            last_point_time = now

            current_touches = assign_ids(prev_touches, points)

            # Limpiar histories de IDs que desaparecieron
            for tid in list(histories.keys()):
                if tid not in current_touches:
                    histories[tid].clear()

            prev_touches = current_touches

            touches_payload = []
            for tid, (x, y) in current_touches.items():
                h = histories[tid]

                speed = ((x - h[-1][0])**2 + (y - h[-1][1])**2)**0.5 if h else 0

                h.append((x, y))

                n = (min(profile["smooth_fast"], len(h))
                     if speed > profile["speed_threshold"]
                     else min(profile["smooth_slow"], len(h)))

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