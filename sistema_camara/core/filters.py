# core/filters.py
# Noah Technology Solutions — Parke Tr3s
# Responsable: Bryan
# Descripción: Implementación del One Euro Filter para suavizar
#              las coordenadas ruidosas de MediaPipe.
#              Se crea una instancia por cada coordenada (x, y, z)
#              de cada landmark del cuerpo.

import math
from sistema_camara.config.settings import (
    ONE_EURO_FREQ,
    ONE_EURO_MINCUTOFF,
    ONE_EURO_BETA,
    ONE_EURO_DCUTOFF
)

# ─────────────────────────────────────────
# FILTRO DE BAJO NIVEL
# ─────────────────────────────────────────
# Este es el bloque base del One Euro Filter.
# Internamente es un filtro de paso bajo — mezcla el valor
# anterior con el nuevo usando un coeficiente alpha.
# Alpha cercano a 1 = confía más en el valor nuevo (menos suavizado)
# Alpha cercano a 0 = confía más en el valor anterior (más suavizado)

class _FiltroPasoBajo:
    def __init__(self, frecuencia: float, cutoff: float):
        self._valor_anterior = None
        self._alfa = self._calcular_alfa(frecuencia, cutoff)

    def _calcular_alfa(self, frecuencia: float, cutoff: float) -> float:
        # Fórmula estándar del One Euro Filter
        te = 1.0 / frecuencia
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / te)

    def aplicar(self, valor: float, alfa: float = None) -> float:
        if alfa is not None:
            self._alfa = alfa

        if self._valor_anterior is None:
            # Primer frame — no hay valor anterior, devuelve el valor tal cual
            self._valor_anterior = valor
            return valor

        # Mezcla el valor anterior con el nuevo
        resultado = self._alfa * valor + (1.0 - self._alfa) * self._valor_anterior
        self._valor_anterior = resultado
        return resultado


# ─────────────────────────────────────────
# ONE EURO FILTER
# ─────────────────────────────────────────
# Este es el filtro completo. Usa dos filtros de paso bajo internamente:
# uno para el valor en sí, y otro para la velocidad del movimiento.
# La velocidad es lo que le permite adaptarse al tipo de movimiento.

class OneEuroFilter:
    def __init__(
        self,
        frecuencia: float  = ONE_EURO_FREQ,
        min_cutoff: float  = ONE_EURO_MINCUTOFF,
        beta: float        = ONE_EURO_BETA,
        d_cutoff: float    = ONE_EURO_DCUTOFF
    ):
        self._frecuencia  = frecuencia
        self._min_cutoff  = min_cutoff
        self._beta        = beta
        self._d_cutoff    = d_cutoff

        # Filtro para el valor principal (coordenada x, y o z)
        self._filtro_valor = _FiltroPasoBajo(frecuencia, min_cutoff)

        # Filtro para la velocidad (qué tan rápido se mueve el punto)
        self._filtro_velocidad = _FiltroPasoBajo(frecuencia, d_cutoff)

        self._valor_anterior = None

    def aplicar(self, valor: float) -> float:
        # ── Paso 1: Calcular la velocidad del movimiento ──
        if self._valor_anterior is None:
            velocidad = 0.0
        else:
            velocidad = (valor - self._valor_anterior) * self._frecuencia

        # ── Paso 2: Suavizar la velocidad para evitar picos bruscos ──
        velocidad_suavizada = self._filtro_velocidad.aplicar(velocidad)

        # ── Paso 3: Calcular cuánto filtrar según la velocidad ──
        # Movimiento rápido → cutoff alto → alpha alto → menos suavizado
        # Movimiento lento  → cutoff bajo → alpha bajo → más suavizado
        cutoff = self._min_cutoff + self._beta * abs(velocidad_suavizada)

        # ── Paso 4: Aplicar el filtro principal con el cutoff calculado ──
        te = 1.0 / self._frecuencia
        tau = 1.0 / (2 * math.pi * cutoff)
        alfa = 1.0 / (1.0 + tau / te)

        resultado = self._filtro_valor.aplicar(valor, alfa)
        self._valor_anterior = valor
        return resultado


# ─────────────────────────────────────────
# FILTRO PARA UN LANDMARK COMPLETO
# ─────────────────────────────────────────
# MediaPipe devuelve cada punto del cuerpo con x, y, z.
# Esta clase agrupa tres OneEuroFilter — uno por coordenada —
# para filtrar un landmark completo de una sola vez.

class FiltroLandmark:
    def __init__(self):
        self.filtro_x = OneEuroFilter()
        self.filtro_y = OneEuroFilter()
        self.filtro_z = OneEuroFilter()

    def aplicar(self, x: float, y: float, z: float) -> tuple:
        return (
            self.filtro_x.aplicar(x),
            self.filtro_y.aplicar(y),
            self.filtro_z.aplicar(z)
        )


# ─────────────────────────────────────────
# FILTRO PARA EL ESQUELETO COMPLETO
# ─────────────────────────────────────────
# MediaPipe devuelve 33 landmarks por frame.
# Esta clase crea un FiltroLandmark por cada uno de los 33 puntos
# y los filtra todos de una sola vez.
# Jean llama a esta clase — no necesita saber nada de lo que hay arriba.

class FiltroEsqueleto:
    TOTAL_LANDMARKS = 33

    def __init__(self):
        # Un filtro independiente por cada punto del cuerpo
        self._filtros = [FiltroLandmark() for _ in range(self.TOTAL_LANDMARKS)]

    def aplicar(self, landmarks: list) -> list:
        """
        Recibe la lista de landmarks crudos de MediaPipe y devuelve
        la misma lista con las coordenadas suavizadas.

        Cada landmark es un objeto con atributos x, y, z, visibility.
        Devuelve una lista de dicts con x, y, z, confidence.
        """
        resultado = []

        for i, landmark in enumerate(landmarks):
            x_filtrado, y_filtrado, z_filtrado = self._filtros[i].aplicar(
                landmark.x,
                landmark.y,
                landmark.z
            )
            resultado.append({
                "x":          round(x_filtrado, 4),
                "y":          round(y_filtrado, 4),
                "z":          round(z_filtrado, 4),
                "confidence": round(landmark.visibility, 4)
            })

        return resultado