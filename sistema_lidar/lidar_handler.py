import time
from typing import Generator, Tuple, Optional
from rplidar import RPLidar, RPLidarException
from config.settings import SERIAL_PORT, MIN_DISTANCE_MM, MAX_DISTANCE_MM


class LidarHandler:
    def __init__(self) -> None:
        self.port: str = SERIAL_PORT
        self.lidar: Optional[RPLidar] = None
        self.connected: bool = False

    def connect(self) -> None:
        try:
            self.lidar = RPLidar(self.port, baudrate=460800)
            time.sleep(0.5)
            self.lidar.start_motor()
            time.sleep(1)
            info = self.lidar.get_info()
            print(f"[LIDAR] Conectado en {self.port} | Info: {info}")
            self.connected = True
        except Exception as e:
            if self.lidar:
                try:
                    self.lidar.stop()
                    self.lidar.stop_motor()
                    self.lidar.disconnect()
                except Exception:
                    pass
            self.connected = False
            self.lidar = None
            print(f"[LIDAR] Error al conectar: {e}")
        try:
            self.lidar = RPLidar(self.port, baudrate=460800)
            time.sleep(0.5)
            self.lidar.start_motor()
            time.sleep(1)
            info = self.lidar.get_info()
            print(f"[LIDAR] Conectado en {self.port} | Info: {info}")
            self.connected = True
        except Exception as e:
            self.connected = False
            self.lidar = None
            print(f"[LIDAR] Error al conectar: {e}")
        try:
            self.lidar = RPLidar(self.port, baudrate=460800)
            time.sleep(0.5)
            info = self.lidar.get_info()
            print(f"[LIDAR] Conectado en {self.port} | Info: {info}")
            self.connected = True
        except Exception as e:
            self.connected = False
            self.lidar = None
            print(f"[LIDAR] Error al conectar: {e}")

    def disconnect(self) -> None:
        if self.lidar:
            try:
                self.lidar.stop()
                self.lidar.stop_motor()
                self.lidar.disconnect()
            except Exception:
                pass
            self.lidar = None
        self.connected = False
        print("[LIDAR] Desconectado")

    def reconnect(self) -> None:
        print("[LIDAR] Reconectando...")
        self.disconnect()
        time.sleep(5)
        self.connect()

    def read_loop(self) -> Generator[Tuple[float, float], None, None]:
        while True:
            if not self.connected:
                self.connect()
                time.sleep(3)
                continue
            try:
                for scan in self.lidar.iter_scans():
                    for (quality, angle, distance) in scan:
                        if quality == 0 or distance == 0:
                            continue
                        if not (MIN_DISTANCE_MM <= distance <= MAX_DISTANCE_MM):
                            continue
                        yield angle, distance
            except (RPLidarException, Exception) as e:
                print(f"[LIDAR] Error en lectura: {e}")
                self.reconnect()