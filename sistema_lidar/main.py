import asyncio
import threading
import sys
sys.path.append("sistema_lidar")

from lidar_handler import LidarHandler
from processor import Processor
from websocket_server import WebSocketServer

handler = LidarHandler()


async def main():
    processor = Processor()
    server = WebSocketServer()
    loop = asyncio.get_running_loop()

    def lidar_thread():
        from collections import deque
        import time
        history = deque(maxlen=6)
        last_point_time = time.monotonic()
        LIFT_THRESHOLD = 0.12

        for angle, distance in handler.read_loop():
            points = processor.process(angle, distance)
            now = time.monotonic()

            if not points:
                if now - last_point_time > LIFT_THRESHOLD:
                    history.clear()
                continue

            for x, y in points:
                # Detectar velocidad de movimiento
                if history:
                    last = history[-1]
                    speed = ((x - last[0])**2 + (y - last[1])**2)**0.5
                else:
                    speed = 0

                history.append((x, y))
                last_point_time = now

                # Movimiento rápido = menos puntos a promediar
                if speed > 80:
                    n = min(2, len(history))
                else:
                    n = len(history)

                recent = list(history)[-n:]
                avg_x = int(sum(p[0] for p in recent) / len(recent))
                avg_y = int(sum(p[1] for p in recent) / len(recent))

                asyncio.run_coroutine_threadsafe(
                    server.broadcast(avg_x, avg_y), loop
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