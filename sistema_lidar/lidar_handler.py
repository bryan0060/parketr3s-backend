import time
import serial
from typing import Generator, Tuple
from pyrplidar import PyRPlidar

from config.settings import SERIAL_PORT, MIN_DISTANCE_MM, MAX_DISTANCE_MM, BAUDRATE


class LidarHandler:
    def __init__(self) -> None:
        self.port: str = SERIAL_PORT
        self.lidar: PyRPlidar | None = None
        self.connected: bool = False

    def _reset_port(self) -> None:
        try:
            s = serial.Serial(self.port, BAUDRATE, timeout=1)
            s.write(b'\xA5\x40')
            time.sleep(2)
            s.reset_input_buffer()
            s.close()
            time.sleep(1)
        except Exception as e:
            print(f"[LIDAR] Reset puerto: {e}")

    def connect(self) -> None:
        try:
            self._reset_port()
            self.lidar = PyRPlidar()
            self.lidar.connect(port=self.port, baudrate=BAUDRATE, timeout=3)
            self.lidar.set_motor_pwm(1023)
            time.sleep(1)
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
                self.lidar.set_motor_pwm(0)
                self.lidar.disconnect()
            except Exception:
                pass
            self.lidar = None
        self.connected = False
        print("[LIDAR] Desconectado")

    def reconnect(self) -> None:
        print("[LIDAR] Reconectando...")
        self.disconnect()
        time.sleep(3)
        self.connect()

    def read_loop(self) -> Generator[Tuple[float, float], None, None]:
        while True:
            if not self.connected:
                self.connect()
                time.sleep(3)
                continue
            try:
                scan_gen = self.lidar.start_scan()
                for scan in scan_gen():
                    if scan.quality == 0 or scan.distance == 0:
                        continue
                    if not (MIN_DISTANCE_MM <= scan.distance <= MAX_DISTANCE_MM):
                        continue
                    yield scan.angle, scan.distance
            except Exception as e:
                print(f"[LIDAR] Error en lectura: {e}")
                self.reconnect()