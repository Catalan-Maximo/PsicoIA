"""
Servidor TCP para PsicoIA.

- Utiliza asyncio para manejar múltiples conexiones de manera concurrente.
- Cada cliente se gestiona en una coroutine independiente (`handle_client`).
- Implementa un modelo de concurrencia basado en I/O no bloqueante.
- Comparte un único puerto TCP para todas las conexiones.
"""

# Importaciones necesarias
import asyncio  # Para concurrencia asíncrona
from app.config import settings  # Configuración del proyecto
from app.utils.logger import get_logger  # Logger configurado
from app.client_handler import handle_client  # Manejador de clientes

# Logger para este módulo
log = get_logger("server")

async def main():
    """
    Punto de entrada principal para el servidor TCP.

    - Configura un socket de escucha no bloqueante con `asyncio.start_server`.
    - Por cada conexión entrante, agenda una coroutine `handle_client`.
    - Registra en logs la dirección y el puerto donde el servidor está escuchando.
    """
    # Crear el servidor TCP
    server = await asyncio.start_server(
        handle_client,  # Función manejadora para cada cliente
        host=settings.APP_HOST,  # Dirección del host (configurable)
        port=settings.APP_PORT,  # Puerto del servidor (configurable)
    )

    # Obtener las direcciones donde el servidor está escuchando
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    log.info(f"TCP server escuchando en {addrs}")

    # Mantener el servidor corriendo indefinidamente
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    # Ejecutar el servidor TCP
    asyncio.run(main())
