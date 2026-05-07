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
        history = deque(maxlen=8)
        
        for angle, distance in handler.read_loop():
            points = processor.process(angle, distance)
            for x, y in points:
                if history:
                    avg_x = sum(p[0] for p in history) / len(history)
                    avg_y = sum(p[1] for p in history) / len(history)
                    dist = ((x - avg_x)**2 + (y - avg_y)**2) ** 0.5
                    if dist > 120:  # Si el punto está muy lejos, es una mano nueva
                        history.clear()
                
                history.append((x, y))
                if len(history) >= 2:
                    avg_x = int(sum(p[0] for p in history) / len(history))
                    avg_y = int(sum(p[1] for p in history) / len(history))
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