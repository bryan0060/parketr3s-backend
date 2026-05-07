from pyrplidar import PyRPlidar
import time

lidar = PyRPlidar()
lidar.connect(port='COM3', baudrate=460800, timeout=3)
lidar.set_motor_pwm(660)
time.sleep(0.5)
print(lidar.get_health())

scan_gen = lidar.start_scan()
for scan in scan_gen():
    if scan.distance > 0:
        print(f"{scan.angle:.1f}° {scan.distance:.0f}mm")
    break

lidar.stop()
lidar.set_motor_pwm(0)
lidar.disconnect()
print("DONE")