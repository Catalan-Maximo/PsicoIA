import asyncio
from app.config import settings
from app.utils.logger import get_logger
from app.utils.rate_limiter import SlidingWindowLimiter
from app.services.llm_client import llm_generate

log = get_logger("client")
SEM_GLOBAL = asyncio.Semaphore(settings.MAX_IN_FLIGHT)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    log.info(f"Conexión de {peer}")
    limiter = SlidingWindowLimiter(settings.RATE_MAX_MESSAGES, settings.RATE_WINDOW_SECONDS)

    greeting = (
        "Bienvenido a PsicoIA.\n"
        "Contame cómo te sentís hoy. Escribí 'salir' para cerrar.\n"
    )
    writer.write(greeting.encode("utf-8"))
    await writer.drain()

    try:
        while True:
            data = await reader.readline()
            if not data:
                break

            msg = data.decode().strip()
            if msg.lower() == "salir":
                writer.write("Gracias por usar PsicoIA. Cuidate!\n".encode("utf-8"))
                await writer.drain()
                break

            if not limiter.allow():
                writer.write("Tranca, demasiados mensajes seguidos. Probá en unos segundos.\n".encode("utf-8"))
                await writer.drain()
                continue

            async with SEM_GLOBAL:
                # Directly call the LLM with a default state (no router logic)
                llm_reply = await llm_generate(msg, "moderada")
                writer.write((llm_reply + "\n").encode("utf-8"))
                await writer.drain()

    except Exception as e:
        log.exception(f"Error con {peer}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        log.info(f"Conexión cerrada {peer}")

