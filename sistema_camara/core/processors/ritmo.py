# core/processors/ritmo.py
# Noah Technology Solutions — Parke Tr3s
# Descripción: Processor del juego Ritmo (Just Dance).
#              Extrae muñecas y tobillos con su confidence score
#              para que el Frontend valide poses contra la coreografía.

class RitmoProcessor:

    # Índices de MediaPipe para los 4 puntos que necesita este juego
    PUNTOS = {
        15: "muneca_izquierda",
        16: "muneca_derecha",
        27: "tobillo_izquierdo",
        28: "tobillo_derecho"
    }

    def procesar(self, landmarks_filtrados: list) -> dict:
        """
        Recibe los 33 landmarks filtrados y devuelve solo
        los 4 puntos que necesita el juego de Ritmo.

        Cada punto incluye x, y y confidence — el Frontend
        usa confidence para ignorar puntos poco confiables.
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