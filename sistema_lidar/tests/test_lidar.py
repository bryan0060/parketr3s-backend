import sys
sys.path.append("sistema_lidar")

from lidar_handler import LidarHandler

def main():
    handler = LidarHandler()
    print("🟢 Leyendo datos...\n")
    try:
        for i, (angle, distance) in enumerate(handler.read_loop()):
            print(f"{angle:.2f}° | {distance:.2f} mm")
            if i >= 200:
                break
    except KeyboardInterrupt:
        pass
    finally:
        handler.disconnect()

if __name__ == "__main__":
    main()