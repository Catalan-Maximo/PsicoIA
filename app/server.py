import asyncio
from app.config import settings
from app.utils.logger import get_logger
from app.client_handler import handle_client

log = get_logger("server")

async def main():
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
