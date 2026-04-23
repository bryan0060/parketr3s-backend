# Parke Tr3s — Backend Interactivo
**Noah Technology Solutions**

Sistema backend en tiempo real para el Módulo Interactivo Premium del parque
de diversiones Parke Tr3s, ubicado en Urabá. Procesa señales de cámara y LiDAR
para alimentar 6 minijuegos proyectados en pared.

---

## Equipo

| Persona | Rol |
|--------|-----|
| Jean   | Backend Core — Lógica Python, MediaPipe, WebSockets |
| Bryan  | Tech Lead — Arquitectura global, filtros matemáticos |
| Farly  | DevOps — Entorno Windows, puertos seriales, calibración física |
| David  | Frontend — React / Phaser (consumidor de la API) |
| Tomás  | Frontend — React / Phaser (consumidor de la API) |

---

## Arquitectura General

Monorepo con dos microservicios Python independientes que corren en paralelo
en un Mini PC local (AMD Ryzen 7 6800U, 32GB RAM, 1TB SSD) en Kiosk Mode.
Logitech Brio 4K → sistema_camara → WebSocket :8080 → Frontend React/Phaser
RPLiDAR          → sistema_lidar  → WebSocket :8081 → Frontend React/Phaser

Cada sistema corre en su propio proceso para evitar el GIL de Python
y aprovechar los 8 núcleos del Ryzen.

---

## Microservicios

### Sistema Cámara (Puerto 8080) — Fase 1
Captura pose humana con MediaPipe (33 landmarks), aplica filtros matemáticos
(One Euro Filter / EMA) y emite JSON a 60 FPS por WebSocket.

Juegos que alimenta:
- **Juego 1 - Ritmo**: coordenadas + confidence score (tipo Just Dance)
- **Juego 2 - Esquive**: ángulo de torso → estado Izquierda/Centro/Derecha
- **Juego 3 - Impacto**: velocidad y aceleración de puños y pies
- **Juego 4 - Poses**: esqueleto completo filtrado para congelar silueta

### Sistema LiDAR (Puerto 8081) — Fase 2 (Semana 3)
Lee el RPLiDAR por puerto serial, convierte coordenadas polares a cartesianas
(X, Y) y emite posición en tiempo real.

Juegos que alimenta:
- **Juego 5 - Pizarra**: trayectoria de mano sobre pared (tipo Magic Canvas)
- **Juego 6 - Penaltis**: punto de impacto de balón físico en la pared

---

## Estructura del Repositorio
parketr3s-backend/
├── sistema_camara/     # Microservicio 1 — activo desde Semana 1
├── sistema_lidar/      # Microservicio 2 — activo desde Semana 3
├── shared/             # Schemas Pydantic y constantes compartidas
├── docs/               # Contrato API y guías de calibración
├── scripts/            # Scripts de instalación y arranque en Windows
├── requirements.txt
└── requirements_lidar.txt

---

## Instalación (Windows — Farly)

```bat
scripts\install_windows.bat
```

Luego editar `.env` con el índice de cámara y puerto COM del LiDAR.

---

## Arranque

```bat
scripts\start_all.bat
```

O manualmente por sistema:
```bash
# Cámara
python sistema_camara/main.py

# LiDAR (Semana 3)
python sistema_lidar/main.py
```

---

## Contrato API

Ver [`docs/api_contract_v1.md`](docs/api_contract_v1.md) — es el JSON
que el Frontend consume. David y Tomás trabajan con un Mock basado en ese
documento mientras el Backend se desarrolla.

---

## Git Flow

- Rama principal de desarrollo: `develop`
- Ramas de features: `feature/nombre-del-feature`
- Formato de commits: Conventional Commits en español