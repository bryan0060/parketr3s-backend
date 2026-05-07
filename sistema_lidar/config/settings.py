from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CALIBRATION_FILE = BASE_DIR / "calibration_matrix.npy"

# LIDAR
SERIAL_PORT = "COM3"
BAUDRATE = 460800

# MOTOR
MOTOR_PWM = 1023          # Más rápido (max 1023)

# FILTROS
MIN_DISTANCE_MM = 50
MAX_DISTANCE_MM = 2000

# PANTALLA
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

# WEBSOCKET
WS_HOST = "0.0.0.0"
WS_PORT = 8081

# FILTRO DE OBJETO
MAX_CLUSTER_ANGLE = 15.0  # Grados máximos que puede ocupar un objeto válido
MIN_CLUSTER_ANGLE = 0.3   # Grados mínimos (descarta ruido)