from sistema_camara.config.settings import (
    ESQUIVE_ZONA_IZQUIERDA,
    ESQUIVE_ZONA_DERECHA,
    ESQUIVE_UMBRAL_AGACHARSE,
    ESQUIVE_FRAMES_CONFIRMACION,
)


class EsquiveProcessor:

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
        self._home_y: float | None = None

    def reset(self):
        self._carril_anterior  = "CENTER"
        self._carril_candidato = "CENTER"
        self._frames_candidato = 0
        self._home_y           = None

    def procesar(self, landmarks_todos: list, modo: str) -> dict:
        landmarks = landmarks_todos[0]

        hombro_izq = landmarks[self.IDX_HOMBRO_IZQ]
        hombro_der = landmarks[self.IDX_HOMBRO_DER]
        cadera_izq = landmarks[self.IDX_CADERA_IZQ]
        cadera_der = landmarks[self.IDX_CADERA_DER]
        muneca_izq = landmarks[self.IDX_MUNECA_IZQ]
        muneca_der = landmarks[self.IDX_MUNECA_DER]

        hip_x = (cadera_izq["x"] + cadera_der["x"]) / 2
        hip_y = (cadera_izq["y"] + cadera_der["y"]) / 2

        shoulder_y   = (hombro_izq["y"] + hombro_der["y"]) / 2
        altura_torso = abs(hip_y - shoulder_y)

        if self._home_y is None:
            self._home_y = hip_y

        dy = (hip_y - self._home_y) / altura_torso if altura_torso > 0.01 else 0.0

        carril = self._calcular_carril(hip_x)
        accion = self._calcular_accion(dy, hombro_izq, hombro_der, muneca_izq, muneca_der)

        if accion == 'IDLE':
            self._home_y = self._home_y * 0.95 + hip_y * 0.05

        if accion == 'CROUCH':
            carril = self._carril_anterior

        return {
            "carril": carril,
            "accion": accion,
            "debug": {
                "hip_x":          round(hip_x,        3),
                "hip_y":          round(hip_y,        3),
                "dy_normalizado": round(dy,            3),
                "home_y":         round(self._home_y,  4),
                "altura_torso":   round(altura_torso,  4),
            }
        }

    def _calcular_carril(self, hip_x: float) -> str:
        if hip_x < ESQUIVE_ZONA_IZQUIERDA:
            candidato = "LEFT"
        elif hip_x > ESQUIVE_ZONA_DERECHA:
            candidato = "RIGHT"
        else:
            candidato = "CENTER"

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
        muneca_izq_arriba = muneca_izq["y"] < hombro_izq["y"]
        muneca_der_arriba = muneca_der["y"] < hombro_der["y"]

        if muneca_izq_arriba and muneca_der_arriba:
            return "JUMP"

        if dy > ESQUIVE_UMBRAL_AGACHARSE:
            return "CROUCH"

        return "IDLE"