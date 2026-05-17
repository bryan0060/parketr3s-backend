# sistema_camara/core/processors/esquive.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan
# Descripción: Processor del juego Esquive (Subway Surfers).
#
#              Detecta 4 estados en 2 ejes independientes:
#                  Carril → LEFT | CENTER | RIGHT
#                  Acción → IDLE | JUMP   | CROUCH
#
#              Lateral  → zonas fijas del frame (0.0 a 1.0)
#              Salto    → ambas muñecas por encima de los hombros
#              Agacharse → caderas bajan físicamente (Y aumenta)

from sistema_camara.config.settings import (
    ESQUIVE_ZONA_IZQUIERDA,
    ESQUIVE_ZONA_DERECHA,
    ESQUIVE_UMBRAL_AGACHARSE,
    ESQUIVE_FRAMES_CONFIRMACION,
)


class EsquiveProcessor:

    # Índices de MediaPipe
    IDX_HOMBRO_IZQ = 11
    IDX_HOMBRO_DER = 12
    IDX_CADERA_IZQ = 23
    IDX_CADERA_DER = 24
    IDX_MUNECA_IZQ = 15
    IDX_MUNECA_DER = 16

    def __init__(self):
        self._carril_anterior  = "CENTER"
        self._carril_candidato = "CENTER"
        self._frames_candidato = 0

        # home_y — se fija en el primer frame solo para agacharse
        self._home_y: float | None = None

    def reset(self):
        """
        Reinicia el estado cuando el jugador sale del frame.
        main.py llama esto cuando jugadores_detectados cae a 0.
        """
        self._carril_anterior  = "CENTER"
        self._carril_candidato = "CENTER"
        self._frames_candidato = 0
        self._home_y           = None

    def procesar(self, landmarks_todos: list, modo: str) -> dict:
        landmarks = landmarks_todos[0]

        # ── Extraer puntos relevantes ──
        hombro_izq = landmarks[self.IDX_HOMBRO_IZQ]
        hombro_der = landmarks[self.IDX_HOMBRO_DER]
        cadera_izq = landmarks[self.IDX_CADERA_IZQ]
        cadera_der = landmarks[self.IDX_CADERA_DER]
        muneca_izq = landmarks[self.IDX_MUNECA_IZQ]
        muneca_der = landmarks[self.IDX_MUNECA_DER]

        # ── Centro de caderas ──
        hip_x = (cadera_izq["x"] + cadera_der["x"]) / 2
        hip_y = (cadera_izq["y"] + cadera_der["y"]) / 2

        # ── home_y: solo para agacharse, se fija una vez ──
        if self._home_y is None:
            self._home_y = hip_y

        # ── Altura del torso como unidad para agacharse ──
        shoulder_y   = (hombro_izq["y"] + hombro_der["y"]) / 2
        altura_torso = abs(hip_y - shoulder_y)
        dy = (hip_y - self._home_y) / altura_torso if altura_torso > 0.01 else 0.0

        # ── Calcular estados ──
        carril = self._calcular_carril(hip_x)
        accion = self._calcular_accion(dy, hombro_izq, hombro_der, muneca_izq, muneca_der)

        return {
            "carril": carril,
            "accion": accion,
            "debug": {
                "hip_x":         round(hip_x,       3),
                "hip_y":         round(hip_y,       3),
                "dy_normalizado": round(dy,          3),
                "home_y":        round(self._home_y, 4),
                "altura_torso":  round(altura_torso, 4),
            }
        }

    def _calcular_carril(self, hip_x: float) -> str:
        """
        Divide el frame en 3 zonas fijas.
        El jugador no necesita moverse desde ningún punto de partida —
        simplemente estar en la zona activa es suficiente.

        0.0 ──── ZONA_IZQ ──── ZONA_DER ──── 1.0
         LEFT      CENTER       CENTER       RIGHT
        """
        if hip_x < ESQUIVE_ZONA_IZQUIERDA:
            candidato = "LEFT"
        elif hip_x > ESQUIVE_ZONA_DERECHA:
            candidato = "RIGHT"
        else:
            candidato = "CENTER"

        # ── Confirmación por frames ──
        if candidato == self._carril_candidato:
            self._frames_candidato += 1
        else:
            self._carril_candidato = candidato
            self._frames_candidato = 1

        if self._frames_candidato >= ESQUIVE_FRAMES_CONFIRMACION:
            self._carril_anterior = self._carril_candidato

        return self._carril_anterior

    def _calcular_accion(
        self,
        dy: float,
        hombro_izq: dict,
        hombro_der: dict,
        muneca_izq: dict,
        muneca_der: dict,
    ) -> str:
        """
        JUMP   → ambas muñecas por encima de sus hombros.
        CROUCH → caderas bajan respecto al home_y.
        """
        muneca_izq_arriba = muneca_izq["y"] < hombro_izq["y"]
        muneca_der_arriba = muneca_der["y"] < hombro_der["y"]

        if muneca_izq_arriba and muneca_der_arriba:
            return "JUMP"

        if dy > ESQUIVE_UMBRAL_AGACHARSE:
            return "CROUCH"

        return "IDLE"