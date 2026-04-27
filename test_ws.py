import asyncio
import websockets
import json

async def escuchar_backend():
    uri = "ws://localhost:8080/ws"
    print(f"⏳ Conectando al backend en {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado. Esperando datos...\n")
            while True:
                respuesta = await websocket.recv()
                datos = json.loads(respuesta)
                
                # Imprimimos un resumen para no saturar la consola
                print(f"FPS: {datos['fps_actual']} | Jugador: {datos['jugador_detectado']} | Puntos extraídos: {len(datos.get('poses', {}).get('esqueleto', {}))}")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    asyncio.run(escuchar_backend())