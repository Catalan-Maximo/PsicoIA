import os
import asyncio
import websockets
from app.config import settings

"""
Gateway WebSocket ↔ TCP:
- Por CADA conexión WebSocket del navegador, se abre UNA conexión TCP propia hacia el server 'app'.
- Mapeo 1:1 (WS cliente) ↔ (TCP cliente) garantiza que sesiones no se mezclen.
- Concurrencia por I/O: websockets.serve() agenda una coroutine por WS; asyncio.open_connection() usa sockets no bloqueantes.
- En Docker, TCP_HOST='app' cablea el socket interno gateway->app por la red del compose.
"""

# --- Configuración de red con valores predeterminados ---
# TCP_HOST: Dirección del servidor TCP al que se conectará el gateway.
# TCP_PORT: Puerto del servidor TCP (por defecto, el puerto definido en settings.APP_PORT).
# WS_HOST: Dirección en la que el gateway escuchará conexiones WebSocket.
# WS_PORT: Puerto en el que el gateway escuchará conexiones WebSocket.
TCP_HOST = os.getenv("TCP_HOST", "127.0.0.1")                 # En Docker usarás 'app'
TCP_PORT = int(os.getenv("TCP_PORT", settings.APP_PORT))      # 5001 por defecto
WS_HOST  = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT  = int(os.getenv("WS_PORT", "8765"))

async def bridge_ws_to_tcp(websocket: websockets.WebSocketServerProtocol):
    """
    Establece un puente entre una conexión WebSocket y una conexión TCP.

    - Por cada cliente WebSocket, se abre una conexión TCP hacia el servidor.
    - Los mensajes del cliente WS se envían al servidor TCP y viceversa.
    - Maneja errores de conexión y asegura el cierre adecuado de sockets.
    """
    try:
        # Intentar abrir una conexión TCP al servidor especificado
        reader, writer = await asyncio.open_connection(TCP_HOST, TCP_PORT)
    except Exception as e:
        # Enviar un mensaje de error al cliente WebSocket si falla la conexión TCP
        await websocket.send(f"[gateway] No pude conectar al TCP {TCP_HOST}:{TCP_PORT}: {e}")
        await websocket.close()
        return

    async def ws_reader():
        """
        Lee mensajes del cliente WebSocket y los envía al servidor TCP.

        - Escribe cada mensaje recibido en el socket TCP.
        - Maneja errores y asegura el cierre del escritor TCP.
        """
        try:
            async for message in websocket:
                writer.write((message.strip() + "\n").encode("utf-8"))
                await writer.drain()  # Asegurar que el mensaje se envíe completamente
        except Exception as e:
            # Manejo de errores en la conexión WebSocket
            pass
        finally:
            try:
                writer.close()  # Cerrar el escritor TCP
                await writer.wait_closed()
            except Exception:
                pass

    async def tcp_reader():
        """
        Lee mensajes del servidor TCP y los envía al cliente WebSocket.

        - Procesa cada línea recibida del servidor TCP.
        - Maneja errores y asegura el cierre del cliente WebSocket.
        """
        try:
            while not reader.at_eof():
                line = await reader.readline()
                if not line:
                    break
                await websocket.send(line.decode("utf-8"))  # Enviar línea al cliente WS
        except Exception:
            pass
        finally:
            try:
                await websocket.close()  # Cerrar el cliente WebSocket
            except Exception:
                pass

    # Ejecutar las tareas de lectura/escritura de WebSocket y TCP en paralelo
    await asyncio.gather(ws_reader(), tcp_reader())

async def main():
    """
    Inicia el servidor WebSocket y lo vincula al puente TCP.

    - Escucha conexiones WebSocket en la dirección y puerto configurados.
    - Por cada conexión WebSocket, se crea una tarea para manejar el puente.
    """
    print(f"[gateway] WS escuchando en ws://{WS_HOST}:{WS_PORT}  ->  TCP {TCP_HOST}:{TCP_PORT}")
    async with websockets.serve(bridge_ws_to_tcp, WS_HOST, WS_PORT, ping_interval=20, ping_timeout=20):
        await asyncio.Future()  # Mantener el servidor corriendo indefinidamente

if __name__ == "__main__":
    # Punto de entrada principal: Ejecutar el servidor WebSocket
    asyncio.run(main())
