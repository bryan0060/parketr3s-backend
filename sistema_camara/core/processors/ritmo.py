# sistema_camara/core/processors/ritmo.py
# Noah Technology Solutions — Parke Tr3s
# Descripción: Processor del juego Ritmo (Just Dance).
#              Extrae muñecas y tobillos con su confidence score
#              para que el Frontend valide poses contra la coreografía.
#              Soporta modo "solo" (1 jugador) y "duo" (2 jugadores).

class RitmoProcessor:

    # Índices de MediaPipe para los 4 puntos que necesita este juego
    PUNTOS = {
        15: "muneca_izquierda",
        16: "muneca_derecha",
        27: "tobillo_izquierdo",
        28: "tobillo_derecho"
    }

    def _extraer_puntos(self, landmarks_filtrados: list) -> dict:
        """
        Recibe los 33 landmarks de un jugador y devuelve solo
        los 4 puntos que necesita el juego de Ritmo.
        """
        resultado = {}
        for indice, nombre in self.PUNTOS.items():
            punto = landmarks_filtrados[indice]
            resultado[nombre] = {
                "x":          punto["x"],
                "y":          punto["y"],
                "confidence": punto["confidence"]
            }
        return resultado

    def procesar(self, landmarks_todos: list, modo: str) -> dict:
        """
        Modo solo:
            { "muneca_izquierda": {...}, ... }

        Modo duo:
            {
                "jugador_1": { "detectado": true, "muneca_izquierda": {...}, ... },
                "jugador_2": { "detectado": true/false, ... }
            }
        """
        if modo == "duo":
            resultado = {
                "jugador_1": {
                    "detectado": True,
                    **self._extraer_puntos(landmarks_todos[0])
                }
            }

            if len(landmarks_todos) >= 2:
                resultado["jugador_2"] = {
                    "detectado": True,
                    **self._extraer_puntos(landmarks_todos[1])
                }
            else:
                resultado["jugador_2"] = {"detectado": False}

            return resultado

        # ── Modo solo — estructura idéntica al contrato original ──
        return self._extraer_puntos(landmarks_todos[0])