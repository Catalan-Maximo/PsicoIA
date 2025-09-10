# app/utils/client_handler.py
import asyncio
import itertools
import time
from app.config import settings
from app.utils.logger import get_logger
from app.utils.rate_limiter import SlidingWindowLimiter
from app.services.llm_client import llm_generate

"""
Multiusuario y aislamiento:
- "Una conexión, una coroutine": cada cliente tiene su propia handle_client() -> no se mezclan estados.
- Etiqueta de conexión: Usuario-N (solo para logs/claridad de demo).
- Rate limit por usuario: SlidingWindowLimiter evita flooding.
- Semáforo global: limita simultáneos contra el LLM (MAX_IN_FLIGHT).
- Asincronismo: await reader.readline(), await writer.drain(), await llm_generate(...)
  ceden control al event loop para atender otras conexiones.
"""

log = get_logger("client")
SEM_GLOBAL = asyncio.Semaphore(settings.MAX_IN_FLIGHT)
USER_SEQ = itertools.count(1)   # Usuario-1, Usuario-2, ...

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    user = f"Usuario-{next(USER_SEQ)}"
    msg_counter = itertools.count(1)  # m1, m2, m3 por conexión
    log.info(f"[{user}] Conexión desde {peer}")

    limiter = SlidingWindowLimiter(
        settings.RATE_MAX_MESSAGES, settings.RATE_WINDOW_SECONDS
    )

    greeting = (
        f"{user} conectado.\n"
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
                writer.write(
                    "Tranca, demasiados mensajes seguidos. Probá en unos segundos.\n".encode("utf-8")
                )
                await writer.drain()
                continue

            async with SEM_GLOBAL:
                # Concurrency y trazabilidad:
                # - 'trace_id' vincula cada request al LLM con el usuario y nro de mensaje (Usuario-X:mY).
                # - Esto permite ver en logs a qué usuario corresponde cada POST y su latencia.
                trace_id = f"{user}:m{next(msg_counter)}"

                t0 = time.perf_counter()
                log.info(f"[{trace_id}] → LLM start (len={len(msg)})")

                # Usamos 'user' como conversation_id para mantener el historial por conexión
                llm_reply = await llm_generate(msg, trace_id=trace_id, conversation_id=user)

                dt_ms = (time.perf_counter() - t0) * 1000
                log.info(f"[{trace_id}] ← LLM ok ({len(llm_reply)} chars) {dt_ms:.0f} ms")

                out = f"{llm_reply}"
                writer.write((out + "\n").encode("utf-8"))
                await writer.drain()

    except Exception as e:
        log.exception(f"[{user}] Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        log.info(f"[{user}] Conexión cerrada")
