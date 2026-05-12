import time
import serial
from typing import Generator, Tuple
from pyrplidar import PyRPlidar
from config.settings import SERIAL_PORT, MIN_DISTANCE_MM, MAX_DISTANCE_MM, BAUDRATE, MOTOR_RPM


class LidarHandler:
    def __init__(self) -> None:
        self.port = SERIAL_PORT
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

    def _motor_speed_command(self, rpm: int) -> bytes:
        rpm_low = rpm & 0xFF
        rpm_high = (rpm >> 8) & 0xFF
        payload_size = 0x02
        cmd_type = 0xA8
        checksum = 0 ^ 0xA5 ^ cmd_type ^ payload_size ^ rpm_low ^ rpm_high
        return bytes([0xA5, cmd_type, payload_size, rpm_low, rpm_high, checksum])

    def _set_motor_speed_rpm(self, rpm: int) -> None:
        try:
            packet = self._motor_speed_command(rpm)
            if self.lidar and hasattr(self.lidar, 'lidar_serial'):
                self.lidar.lidar_serial._serial.write(packet)
            else:
                s = serial.Serial(self.port, BAUDRATE, timeout=1)
                s.write(packet)
                time.sleep(0.1)
                s.close()
            print(f"[LIDAR] Velocidad motor: {rpm} RPM")
        except Exception as e:
            print(f"[LIDAR] Error al setear RPM: {e}")

    def connect(self) -> None:
        try:
            self._reset_port()
            self._set_motor_speed_rpm(MOTOR_RPM)
            self.lidar = PyRPlidar()
            self.lidar.connect(port=self.port, baudrate=BAUDRATE, timeout=3)
            self._set_motor_speed_rpm(MOTOR_RPM)
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
                self._set_motor_speed_rpm(0)
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
                self._set_motor_speed_rpm(MOTOR_RPM)
                for scan in scan_gen():
                    if scan.distance == 0:
                        continue
                    if not (MIN_DISTANCE_MM <= scan.distance <= MAX_DISTANCE_MM):
                        continue
                    if hasattr(scan, 'start_flag') and scan.start_flag:
                        now = time.monotonic()
                        if hasattr(self, '_last_start') and self._last_start:
                            delta = now - self._last_start
                            print(f"[LIDAR] RPM: {(1/delta)*60:.1f}")
                        self._last_start = now
                    yield scan.angle, scan.distance
            except Exception as e:
                print(f"[LIDAR] Error en lectura: {e}")
                self.reconnect()