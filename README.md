# 🔴 Sistema LiDAR — Puerto 8081
**Noah Technology Solutions — Parke Tr3s**
**Responsable: Jean**

---

## ¿Qué es este sistema?

El sistema LiDAR es el microservicio 2 del backend. Corre completamente
independiente del sistema de cámara en el puerto 8081 y alimenta 2 juegos:

- **Pizarra Mágica** — coordenadas X, Y de la mano sobre la pared
- **Penaltis** — punto exacto de impacto del balón físico en la pared

---

## ¿Qué debe construir?

En este orden exacto — no saltar al siguiente sin terminar el anterior:

**1. `core/websocket_server.py`**
Servidor WebSocket en el puerto 8081. Misma estructura que
`sistema_camara/core/websocket_server.py` — léalo primero.

**2. `core/processors/pizarra.py`**
Devuelve coordenadas X, Y fluidas de la mano sobre la pared.

**3. `core/processors/penaltis.py`**
Devuelve el punto exacto de impacto y si hubo impacto detectado.

**4. `main.py`**
Orquestador principal. Misma estructura que `sistema_camara/main.py`.

---

## Referencia obligatoria

Antes de escribir una sola línea leer estos archivos del sistema de cámara:

```
sistema_camara/core/websocket_server.py
sistema_camara/core/processors/poses.py
sistema_camara/main.py
```

El sistema LiDAR sigue exactamente la misma arquitectura. No inventar nada nuevo.

---

## JSON que debe emitir el puerto 8081

**Pizarra Mágica:**
```json
{
  "timestamp": 1719500000.123,
  "juego_activo": "pizarra",
  "sensor_activo": true,
  "fps_actual": 30.0,
  "pizarra": {
    "x": 0.45,
    "y": 0.32
  }
}
```

**Penaltis:**
```json
{
  "timestamp": 1719500000.123,
  "juego_activo": "penaltis",
  "sensor_activo": true,
  "fps_actual": 30.0,
  "penaltis": {
    "x": 0.67,
    "y": 0.58,
    "impacto_detectado": true
  }
}
```



## Estructura de carpetas a crear

```
sistema_lidar/
├── core/
│   ├── __init__.py
│   ├── websocket_server.py
│   └── processors/
│       ├── __init__.py
│       ├── pizarra.py
│       └── penaltis.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── utils/
│   ├── __init__.py
│   └── logger.py
├── tests/
├── main.py
└── README.md        ← estás aquí
```

---

## Git Flow

Trabajar siempre en la rama `feature/sistema-lidar`. Nunca en `develop`.

```bash
# Antes de arrancar cada día
git checkout feature/sistema-lidar
git pull origin feature/sistema-lidar

# Cuando algo funciona y está probado
git add .
git commit -m "feat(lidar): descripción de lo que hizo"
git push origin feature/sistema-lidar
```

Avisar a Bryan cuando algo esté listo para revisión antes de hacer merge a `develop`.

---

## Reglas

- Nunca hacer push a `develop` directamente
- Nunca hacer push a `main`