# ⚙️ Parke Tr3s — Backend Interactivo

Proyecto desarrollado por **Noah Technology Solutions** para **Parke Tr3s**.
Backend en tiempo real que procesa señales de cámara y LiDAR para alimentar
6 minijuegos proyectados en una pared, corriendo 24/7 en un Mini PC en Kiosk Mode.

---

## 👥 Equipo

| Rol | Nombre | Responsabilidad |
|---|---|---|
| Tech Lead | Bryan | Arquitectura global, filtros matemáticos, revisión |
| Backend Core | Jean | Lógica Python, MediaPipe, WebSockets |
| DevOps | Farly | Entorno Windows, puertos seriales, calibración física |

> David y Tomás son el equipo de Frontend. Ellos consumen la data que este backend emite.

---

## 🧱 Stack

- **Python 3.11+** — Lenguaje principal
- **FastAPI + Uvicorn** — Servidor WebSocket
- **MediaPipe** — Detección de pose corporal (33 landmarks)
- **OpenCV** — Captura de la Logitech Brio 4K
- **NumPy** — Filtros matemáticos y cálculos geométricos
- **Pydantic** — Validación y estructura del JSON que recibe el Frontend

---

## 🎮 Los 6 juegos y qué procesa el backend

Hay 2 sensores físicos. Cada uno corre como un proceso Python independiente
con su propio puerto WebSocket:

### 📷 Sistema Cámara → Puerto 8080 (Fase 1 — activo desde Semana 1)

| Juego | Qué calcula el backend | Estado |
|---|---|---|
| Ritmo (Just Dance) | Coordenadas + confidence score de muñecas y tobillos | 🔴 Pendiente |
| Esquive (Subway Surfers) | Ángulo del torso → estado `LEFT / CENTER / RIGHT` | 🔴 Pendiente |
| Impacto (Fruit Ninja) | Velocidad y aceleración de puños y pies | 🔴 Pendiente |
| Poses (Duro contra el Muro) | Esqueleto completo filtrado sin temblor | 🔴 Pendiente |

### 🔴 Sistema LiDAR → Puerto 8081 (Fase 2 — activo desde Semana 3)

| Juego | Qué calcula el backend | Estado |
|---|---|---|
| Pizarra Mágica | Coordenadas X, Y fluidas de la mano sobre la pared | 🔴 Pendiente |
| Penaltis | Punto exacto de impacto del balón físico en la pared | 🔴 Pendiente |

---

## 📁 Estructura del proyecto

```
parketr3s-backend/
├── sistema_camara/               ← Microservicio 1 (activo)
│   ├── core/
│   │   ├── capture.py            ← [Jean] Captura Brio + MediaPipe
│   │   ├── filters.py            ← [Bryan] One Euro Filter / EMA
│   │   ├── websocket_server.py   ← [Jean] Servidor WS en puerto 8080
│   │   └── processors/
│   │       ├── ritmo.py
│   │       ├── esquive.py
│   │       ├── impacto.py
│   │       └── poses.py
│   ├── config/
│   │   └── settings.py           ← FPS, resolución, umbrales, puerto
│   ├── utils/
│   │   ├── math_helpers.py       ← [Bryan] Geometría reutilizable
│   │   └── logger.py
│   ├── tests/
│   └── main.py                   ← Entrypoint: python main.py
├── sistema_lidar/                ← Microservicio 2 (Semana 3)
│   └── README.md
├── shared/
│   ├── schemas.py                ← Modelos Pydantic / contratos JSON
│   └── constants.py              ← Enums globales
├── docs/
│   └── api_contract_v1.md        ← JSON exacto que consume el Frontend
├── scripts/
│   ├── install_windows.bat       ← Setup completo en el Mini PC
│   └── start_all.bat             ← Arranca ambos microservicios
├── .env.example
├── requirements.txt              ← Dependencias del sistema cámara
└── requirements_lidar.txt        ← Dependencias del LiDAR (instalar en Semana 3)
```

parketr3s-backend/
├── sistema_camara/               ← Microservicio 1 (activo)
│   ├── core/
│   │   ├── capture.py            ← [Jean] Captura Brio + MediaPipe
│   │   ├── filters.py            ← [Bryan] One Euro Filter / EMA
│   │   ├── websocket_server.py   ← [Jean] Servidor WS en puerto 8080
│   │   └── processors/           ← Un archivo por juego
│   │       ├── ritmo.py
│   │       ├── esquive.py
│   │       ├── impacto.py
│   │       └── poses.py
│   ├── config/
│   │   └── settings.py           ← FPS, resolución, umbrales, puerto
│   ├── utils/
│   │   ├── math_helpers.py       ← [Bryan] Geometría reutilizable
│   │   └── logger.py
│   ├── tests/
│   └── main.py                   ← Entrypoint: python main.py
├── sistema_lidar/                ← Microservicio 2 (Semana 3)
│   └── README.md
├── shared/
│   ├── schemas.py                ← Modelos Pydantic / contratos JSON
│   └── constants.py              ← Enums globales
├── docs/
│   └── api_contract_v1.md        ← JSON exacto que consume el Frontend
├── scripts/
│   ├── install_windows.bat       ← Setup completo en el Mini PC
│   └── start_all.bat             ← Arranca ambos microservicios
├── .env.example
├── requirements.txt              ← Dependencias del sistema cámara
└── requirements_lidar.txt        ← Dependencias del LiDAR (instalar en Semana 3)

---

## 🚀 Cómo correr el proyecto

**Requisitos previos**
- Python 3.11+ → https://www.python.org/downloads/
- Git → https://git-scm.com/download/win
- Logitech Brio 4K conectada (plug & play en Windows 11)

```bash
# 1. Clonar el repositorio
git clone <URL-del-repo>
cd parketr3s-backend

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.example .env
# Abrir .env y ajustar:
# CAMARA_INDEX → índice de la cámara (normalmente 0)
# LIDAR_PUERTO_SERIAL → puerto COM del RPLiDAR (ej: COM3)

# 4. Arrancar
python sistema_camara/main.py
```

> En Semana 3, para el LiDAR:
> `pip install -r requirements_lidar.txt` y luego `python sistema_lidar/main.py`

---

## 🌿 Git Flow

| Rama | Uso |
|---|---|
| `main` | Versión instalada en el Mini PC del parque. **No tocar.** |
| `develop` | Rama de trabajo. Hacer push aquí siempre. |

```bash
# Antes de empezar — siempre
git pull origin develop

# Cuando algo funciona
git add .
git commit -m "feat(sistema): descripción de lo que hiciste"
git push origin develop
```

---

## 📄 Contrato API

El archivo `docs/api_contract_v1.md` tiene el JSON exacto que este backend
le envía al Frontend. David y Tomás trabajan con un Mock basado en ese
documento mientras el backend se desarrolla en paralelo.

---

## ✅ Estado del proyecto

| Fase | Estado | Descripción |
|---|---|---|
| Estructura del monorepo | ✅ Completa | Carpetas, requirements, scripts |
| Contrato API (JSON) | 🟡 En progreso | Paso 2 |
| Captura Brio + MediaPipe | 🔴 Pendiente | Paso 3 |
| Filtros matemáticos | 🔴 Pendiente | Paso 3 |
| Processors (4 juegos cámara) | 🔴 Pendiente | Semanas 1-2 |
| Sistema LiDAR | 🔴 Pendiente | Semana 3 |
| Build final en Mini PC | 🔴 Pendiente | Semana 5 |