import asyncio
from app.config import settings
from app.utils.logger import get_logger
from app.client_handler import handle_client

"""
Modelo de concurrencia y sockets (server TCP):
- Un SOLO proceso y un SOLO hilo principal con asyncio (no usamos hilos ni procesos por cliente).
- asyncio.start_server() acepta conexiones y para CADA cliente agenda una coroutine handle_client().
- Todas las conexiones comparten el mismo puerto TCP (5001). No hay un puerto por usuario.
- Concurrencia por I/O no bloqueante: mientras una conexión espera I/O (leer socket o Groq), el loop atiende otras.
- Backpressure / protección: un semáforo global (MAX_IN_FLIGHT) limita tareas simultáneas.
"""

log = get_logger("server")

async def main():
    # Concurrency desde la red:
    # - start_server() mantiene un socket de escucha no bloqueante.
    # - Por cada conexión entrante, crea y agenda una coroutine independiente handle_client().
    server = await asyncio.start_server(
        handle_client,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
    )
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    log.info(f"TCP server escuchando en {addrs}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
