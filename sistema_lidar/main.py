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
        for angle, distance in handler.read_loop():
            point = processor.process(angle, distance)
            if point:
                x, y = point
                asyncio.run_coroutine_threadsafe(
                    server.broadcast(x, y), loop
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