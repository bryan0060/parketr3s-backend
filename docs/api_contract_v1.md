1. Contrato API actualizado — pégalo en docs/:
markdown# Contrato API v2 — Sistema Cámara Puerto 8080
**Noah Technology Solutions — Parke Tr3s**
Última actualización: Semana 4

---

## Cambios respecto a v1
- `jugador_detectado` (bool) → `jugadores_detectados` (int: 0, 1 o 2)
- Se agrega campo `"modo": "solo" | "duo"` en todos los mensajes
- Poses y Ritmo ahora soportan modo duo
- Esquive e Impacto solo soportan modo solo

## Cómo cambiar juego y modo
El frontend manda por WebSocket:
`{"juego": "poses", "modo": "duo"}`
Si no se manda "modo", el default es "solo".

---

## Estructura general
```json
{
  "timestamp": 1719500000.123,
  "juego_activo": "poses",
  "modo": "solo",
  "jugadores_detectados": 1,
  "fps_actual": 59.8,
  "poses": { ... }
}
```

## Juego 1 — Ritmo (modo solo)
```json
{
  "ritmo": {
    "muneca_izquierda":  { "x": 0.42, "y": 0.61, "confidence": 0.97 },
    "muneca_derecha":    { "x": 0.71, "y": 0.58, "confidence": 0.95 },
    "tobillo_izquierdo": { "x": 0.38, "y": 0.91, "confidence": 0.88 },
    "tobillo_derecho":   { "x": 0.63, "y": 0.90, "confidence": 0.91 }
  }
}
```

## Juego 1 — Ritmo (modo duo)
```json
{
  "ritmo": {
    "jugador_1": {
      "detectado": true,
      "muneca_izquierda":  { "x": 0.42, "y": 0.61, "confidence": 0.97 },
      "muneca_derecha":    { "x": 0.71, "y": 0.58, "confidence": 0.95 },
      "tobillo_izquierdo": { "x": 0.38, "y": 0.91, "confidence": 0.88 },
      "tobillo_derecho":   { "x": 0.63, "y": 0.90, "confidence": 0.91 }
    },
    "jugador_2": {
      "detectado": true,
      "muneca_izquierda":  { "x": 0.55, "y": 0.62, "confidence": 0.94 },
      "muneca_derecha":    { "x": 0.80, "y": 0.59, "confidence": 0.92 },
      "tobillo_izquierdo": { "x": 0.51, "y": 0.90, "confidence": 0.89 },
      "tobillo_derecho":   { "x": 0.76, "y": 0.91, "confidence": 0.90 }
    }
  }
}
```

## Juego 2 — Esquive (sin cambios)
```json
{
  "esquive": {
    "carril": "CENTER",
    "angulo_torso": -12.4
  }
}
```

## Juego 3 — Impacto (sin cambios)
```json
{
  "impacto": {
    "mano_izquierda":  { "x": 0.38, "y": 0.45, "velocidad": 2.1,  "aceleracion": 15.7,  "golpe_detectado": false },
    "mano_derecha":    { "x": 0.71, "y": 0.42, "velocidad": 18.9, "aceleracion": 210.3, "golpe_detectado": true  },
    "pie_izquierdo":   { "x": 0.39, "y": 0.89, "velocidad": 0.3,  "aceleracion": 1.1,   "golpe_detectado": false },
    "pie_derecho":     { "x": 0.62, "y": 0.88, "velocidad": 0.5,  "aceleracion": 2.0,   "golpe_detectado": false }
  }
}
```

## Juego 4 — Poses (modo solo, sin cambios)
```json
{
  "poses": {
    "esqueleto": {
      "nariz":             { "x": 0.50, "y": 0.12, "confidence": 0.99 },
      "hombro_izquierdo":  { "x": 0.38, "y": 0.28, "confidence": 0.97 },
      "hombro_derecho":    { "x": 0.62, "y": 0.27, "confidence": 0.96 },
      "codo_izquierdo":    { "x": 0.30, "y": 0.42, "confidence": 0.94 },
      "codo_derecho":      { "x": 0.70, "y": 0.41, "confidence": 0.93 },
      "muneca_izquierda":  { "x": 0.22, "y": 0.55, "confidence": 0.91 },
      "muneca_derecha":    { "x": 0.78, "y": 0.54, "confidence": 0.90 },
      "cadera_izquierda":  { "x": 0.41, "y": 0.55, "confidence": 0.98 },
      "cadera_derecha":    { "x": 0.59, "y": 0.55, "confidence": 0.97 },
      "rodilla_izquierda": { "x": 0.39, "y": 0.73, "confidence": 0.95 },
      "rodilla_derecha":   { "x": 0.61, "y": 0.72, "confidence": 0.94 },
      "tobillo_izquierdo": { "x": 0.38, "y": 0.91, "confidence": 0.92 },
      "tobillo_derecho":   { "x": 0.62, "y": 0.90, "confidence": 0.91 }
    }
  }
}
```

## Juego 4 — Poses (modo duo)
```json
{
  "poses": {
    "jugador_1": {
      "detectado": true,
      "esqueleto": {
        "nariz":             { "x": 0.30, "y": 0.12, "confidence": 0.99 },
        "hombro_izquierdo":  { "x": 0.18, "y": 0.28, "confidence": 0.97 },
        "hombro_derecho":    { "x": 0.42, "y": 0.27, "confidence": 0.96 },
        "codo_izquierdo":    { "x": 0.10, "y": 0.42, "confidence": 0.94 },
        "codo_derecho":      { "x": 0.50, "y": 0.41, "confidence": 0.93 },
        "muneca_izquierda":  { "x": 0.02, "y": 0.55, "confidence": 0.91 },
        "muneca_derecha":    { "x": 0.58, "y": 0.54, "confidence": 0.90 },
        "cadera_izquierda":  { "x": 0.21, "y": 0.55, "confidence": 0.98 },
        "cadera_derecha":    { "x": 0.39, "y": 0.55, "confidence": 0.97 },
        "rodilla_izquierda": { "x": 0.19, "y": 0.73, "confidence": 0.95 },
        "rodilla_derecha":   { "x": 0.41, "y": 0.72, "confidence": 0.94 },
        "tobillo_izquierdo": { "x": 0.18, "y": 0.91, "confidence": 0.92 },
        "tobillo_derecho":   { "x": 0.42, "y": 0.90, "confidence": 0.91 }
      }
    },
    "jugador_2": {
      "detectado": true,
      "esqueleto": {
        "nariz":             { "x": 0.70, "y": 0.13, "confidence": 0.98 },
        "hombro_izquierdo":  { "x": 0.58, "y": 0.29, "confidence": 0.96 },
        "hombro_derecho":    { "x": 0.82, "y": 0.28, "confidence": 0.95 },
        "codo_izquierdo":    { "x": 0.50, "y": 0.43, "confidence": 0.93 },
        "codo_derecho":      { "x": 0.90, "y": 0.42, "confidence": 0.92 },
        "muneca_izquierda":  { "x": 0.42, "y": 0.56, "confidence": 0.90 },
        "muneca_derecha":    { "x": 0.98, "y": 0.55, "confidence": 0.89 },
        "cadera_izquierda":  { "x": 0.61, "y": 0.56, "confidence": 0.97 },
        "cadera_derecha":    { "x": 0.79, "y": 0.56, "confidence": 0.96 },
        "rodilla_izquierda": { "x": 0.59, "y": 0.74, "confidence": 0.94 },
        "rodilla_derecha":   { "x": 0.81, "y": 0.73, "confidence": 0.93 },
        "tobillo_izquierdo": { "x": 0.58, "y": 0.92, "confidence": 0.91 },
        "tobillo_derecho":   { "x": 0.82, "y": 0.91, "confidence": 0.90 }
      }
    }
  }
}
```

## Notas importantes
- `jugador_1` siempre es el de la izquierda en cámara
- Si solo hay 1 persona en modo duo: `jugador_2.detectado: false`, `jugador_2.esqueleto: null`
- LiDAR sigue en puerto 8081 (sin cambios)

2. Prompt para el chat nuevo de frontend:
Somos Noah Technology Solutions, proyecto Parke Tr3s.

Stack frontend: Phaser 3, JavaScript. Es un juego de parque físico con sensores.

El backend emite datos por WebSocket en puerto 8080 (cámara/esqueleto) y puerto 8081 (LiDAR). Ya está terminado.

Hay 4 juegos:
- Ritmo (Just Dance): modo solo y duo
- Esquive (Subway Surfers): solo
- Impacto (golpes a animales): solo
- Poses / "Duro contra el Muro": modo solo y duo. En duo, 2 jugadores cooperan para coincidir juntos con una silueta en pantalla.

El frontend le dice al backend qué juego y modo activar mandando:
{"juego": "poses", "modo": "duo"}