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

# --- Config (con defaults sensatos para correr LOCAL) ---
TCP_HOST = os.getenv("TCP_HOST", "127.0.0.1")                 # en Docker usarás 'app'
TCP_PORT = int(os.getenv("TCP_PORT", settings.APP_PORT))      # 5001 por defecto
WS_HOST  = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT  = int(os.getenv("WS_PORT", "8765"))

async def bridge_ws_to_tcp(websocket: websockets.WebSocketServerProtocol):
    # Se abre la conexión TCP cuando llega un cliente WS
    try:
        reader, writer = await asyncio.open_connection(TCP_HOST, TCP_PORT)
    except Exception as e:
        await websocket.send(f"[gateway] No pude conectar al TCP {TCP_HOST}:{TCP_PORT}: {e}")
        await websocket.close()
        return

    async def ws_reader():
        try:
            async for message in websocket:
                writer.write((message.strip() + "\n").encode("utf-8"))
                await writer.drain()
        except Exception as e:
            # socket WS se cerró o falló
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def tcp_reader():
        try:
            while not reader.at_eof():
                line = await reader.readline()
                if not line:
                    break
                await websocket.send(line.decode("utf-8"))
        except Exception:
            pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    await asyncio.gather(ws_reader(), tcp_reader())

async def main():
    print(f"[gateway] WS escuchando en ws://{WS_HOST}:{WS_PORT}  ->  TCP {TCP_HOST}:{TCP_PORT}")
    async with websockets.serve(bridge_ws_to_tcp, WS_HOST, WS_PORT, ping_interval=20, ping_timeout=20):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
