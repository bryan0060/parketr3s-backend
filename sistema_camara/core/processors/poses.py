# sistema_camara/core/processors/poses.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Jean / Bryan
# Descripción: Extrae los puntos clave del esqueleto para "Duro contra el Muro".
#              Soporta modo "solo" (1 jugador) y "duo" (2 jugadores cooperativos).

class PosesProcessor:
    # Mapeo de índices de MediaPipe a los nombres del contrato API
    MAPEO_LANDMARKS = {
        0:  "nariz",
        11: "hombro_izquierdo",
        12: "hombro_derecho",
        13: "codo_izquierdo",
        14: "codo_derecho",
        15: "muneca_izquierda",
        16: "muneca_derecha",
        23: "cadera_izquierda",
        24: "cadera_derecha",
        25: "rodilla_izquierda",
        26: "rodilla_derecha",
        27: "tobillo_izquierdo",
        28: "tobillo_derecho"
    }

    def _extraer_esqueleto(self, landmarks_filtrados: list) -> dict:
        """
        Toma los 33 landmarks de un jugador y devuelve solo
        los 13 que necesita el juego de Poses.
        """
        esqueleto = {}
        for indice, nombre in self.MAPEO_LANDMARKS.items():
            esqueleto[nombre] = landmarks_filtrados[indice]
        return esqueleto

    def procesar(self, landmarks_todos: list, modo: str) -> dict:
        """
        Modo solo:
            { "esqueleto": { ... } }

        Modo duo:
            {
                "jugador_1": { "detectado": true, "esqueleto": { ... } },
                "jugador_2": { "detectado": true/false, "esqueleto": { ... } | null }
            }
        """
        if modo == "duo":
            resultado = {
                "jugador_1": {
                    "detectado": True,
                    "esqueleto": self._extraer_esqueleto(landmarks_todos[0])
                }
            }

            if len(landmarks_todos) >= 2:
                resultado["jugador_2"] = {
                    "detectado": True,
                    "esqueleto": self._extraer_esqueleto(landmarks_todos[1])
                }
            else:
                resultado["jugador_2"] = {
                    "detectado": False,
                    "esqueleto": None
                }

            return resultado

        # ── Modo solo — estructura idéntica al contrato original ──
        return {"esqueleto": self._extraer_esqueleto(landmarks_todos[0])}