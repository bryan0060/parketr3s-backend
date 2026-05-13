# core/processors/impacto.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan
# Descripción: Processor del juego Impacto (Trixxie vs Animales).
#              Calcula velocidad y aceleración de manos y pies
#              para detectar golpes secos y rápidos.
#              El Frontend decide qué animal responde a qué extremidad.

import math
from sistema_camara.config.settings import (
    IMPACTO_UMBRAL_VELOCIDAD,
    IMPACTO_UMBRAL_ACELERACION
)

class ImpactoProcessor:

    # Índices de MediaPipe para manos y pies
    PUNTOS = {
        15: "mano_izquierda",
        16: "mano_derecha",
        27: "pie_izquierdo",
        28: "pie_derecho"
    }

    def __init__(self):
        # Guardamos el estado anterior de cada punto
        # para poder calcular velocidad y aceleración entre frames
        self._estado_anterior = {
            nombre: {"x": 0.0, "y": 0.0, "velocidad": 0.0}
            for nombre in self.PUNTOS.values()
        }

    def procesar(self, landmarks_todos: list, modo: str) -> dict:
        landmarks_filtrados = landmarks_todos[0]
        """
        Recibe los 33 landmarks filtrados y devuelve velocidad,
        aceleración y si hubo golpe para manos y pies.

        El Frontend usa golpe_detectado + x,y para validar
        si el golpe tocó algún animal en pantalla.
        """
        resultado = {}

        for indice, nombre in self.PUNTOS.items():
            punto    = landmarks_filtrados[indice]
            anterior = self._estado_anterior[nombre]

            # ── Velocidad ──
            # Distancia euclidiana entre posición actual y anterior
            distancia = math.sqrt(
                (punto["x"] - anterior["x"]) ** 2 +
                (punto["y"] - anterior["y"]) ** 2
            )
            velocidad = distancia

            # ── Aceleración ──
            # Cambio brusco de velocidad en un solo frame
            # Un golpe real produce un pico enorme aquí
            aceleracion = abs(velocidad - anterior["velocidad"])

            # ── Detección de golpe ──
            # Ambos umbrales deben superarse al mismo tiempo
            # Solo velocidad alta genera falsos positivos
            # La aceleración confirma que fue un golpe real
            golpe_detectado = (
                velocidad   > IMPACTO_UMBRAL_VELOCIDAD and
                aceleracion > IMPACTO_UMBRAL_ACELERACION
            )

            resultado[nombre] = {
                "x":               punto["x"],
                "y":               punto["y"],
                "velocidad":       round(velocidad,   4),
                "aceleracion":     round(aceleracion, 4),
                "golpe_detectado": golpe_detectado
            }

            # ── Actualizar estado ──
            self._estado_anterior[nombre] = {
                "x":        punto["x"],
                "y":        punto["y"],
                "velocidad": velocidad
            }

        return resultado