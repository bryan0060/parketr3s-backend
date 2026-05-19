# sistema_camara/core/processors/impacto.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan
# Descripción: Processor del juego Salva a Tr3zy.
#              Manda la posición X,Y de ambas manos en tiempo real
#              para que el frontend mueva las redes de caza.

class ImpactoProcessor:

    # Índices de MediaPipe
    IDX_MUNECA_IZQ = 15
    IDX_MUNECA_DER = 16

    def procesar(self, landmarks_todos: list, modo: str) -> dict:
        landmarks = landmarks_todos[0]

        muneca_izq = landmarks[self.IDX_MUNECA_IZQ]
        muneca_der = landmarks[self.IDX_MUNECA_DER]

        return {
            "mano_izquierda": {
                "x":       round(muneca_izq["x"], 4),
                "y":       round(muneca_izq["y"], 4),
                "visible": muneca_izq["confidence"] > 0.5
            },
            "mano_derecha": {
                "x":       round(muneca_der["x"], 4),
                "y":       round(muneca_der["y"], 4),
                "visible": muneca_der["confidence"] > 0.5
            }
        }