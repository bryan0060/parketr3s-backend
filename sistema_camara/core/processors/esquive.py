# core/processors/esquive.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan
# Descripción: Processor del juego Esquive (Subway Surfers).
#              Calcula el ángulo de inclinación del torso usando
#              la posición de los hombros y devuelve el carril
#              activo: LEFT, CENTER o RIGHT.

import math
from sistema_camara.config.settings import ESQUIVE_UMBRAL_ANGULO

class EsquiveProcessor:

    # Índices de MediaPipe
    IDX_HOMBRO_IZQ = 11
    IDX_HOMBRO_DER = 12

    def procesar(self, landmarks_todos: list, modo: str) -> dict:
        landmarks_filtrados = landmarks_todos[0]
        """
        Recibe los 33 landmarks filtrados y devuelve el carril
        activo y el ángulo del torso.
        """
        hombro_izq = landmarks_filtrados[self.IDX_HOMBRO_IZQ]
        hombro_der = landmarks_filtrados[self.IDX_HOMBRO_DER]

        angulo = self._calcular_angulo(hombro_izq, hombro_der)
        carril = self._determinar_carril(angulo)

        return {
            "carril":       carril,
            "angulo_torso": round(angulo, 2)
        }

    def _calcular_angulo(self, hombro_izq: dict, hombro_der: dict) -> float:
        """
        Calcula el ángulo de inclinación del torso en grados.

        En MediaPipe las coordenadas Y crecen hacia abajo.
        Si el hombro izquierdo tiene Y menor, está más arriba
        en pantalla — el jugador se inclinó hacia la derecha.

        Ángulo positivo = inclinado a la derecha (RIGHT)
        Ángulo negativo = inclinado a la izquierda (LEFT)
        Ángulo cercano a 0 = recto (CENTER)
        """
        delta_x = hombro_der["x"] - hombro_izq["x"]
        delta_y = hombro_der["y"] - hombro_izq["y"]

        # atan2 devuelve el ángulo en radianes — convertimos a grados
        angulo_radianes = math.atan2(delta_y, delta_x)
        angulo_grados   = math.degrees(angulo_radianes)

        return angulo_grados

    def _determinar_carril(self, angulo: float) -> str:
        """
        Convierte el ángulo en un estado de carril.
        El umbral viene de settings.py — Farly lo ajusta
        físicamente en el parque.
        """
        if angulo > ESQUIVE_UMBRAL_ANGULO:
            return "RIGHT"
        elif angulo < -ESQUIVE_UMBRAL_ANGULO:
            return "LEFT"
        else:
            return "CENTER"