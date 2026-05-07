from typing import TypedDict

class LidarHitPayload(TypedDict):
    """
    Contrato estricto para los eventos del RPLiDAR (Puerto 8081).
    Alineado con el event.detail esperado por las escenas de Phaser 4.
    """
    tipo_evento: str # El frontend espera esta clave exacta (ej. "hit")
    x: int           # Coordenada X exacta en la resolución de pantalla
    y: int           # Coordenada Y exacta en la resolución de pantalla
    timestamp: int   # Opcional para el frontend, pero vital para logs del backend