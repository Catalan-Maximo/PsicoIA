# app/utils/client_handler.py
"""
Manejador de clientes TCP para PsicoIA.

- Cada cliente tiene su propia coroutine `handle_client`, asegurando aislamiento de estados.
- Implementa control de tasa por usuario con `SlidingWindowLimiter`.
- Usa un semáforo global para limitar solicitudes simultáneas al LLM.
- Proporciona trazabilidad detallada en logs con identificadores únicos por mensaje.
"""

# Importaciones necesarias
import asyncio  # Para concurrencia asíncrona
import itertools  # Para generar identificadores únicos
import time  # Para medir latencia
from app.config import settings  # Configuración del proyecto
from app.utils.logger import get_logger  # Logger configurado
from app.utils.rate_limiter import SlidingWindowLimiter  # Limitador de tasa
from app.services.llm_client import llm_generate  # Cliente para el LLM

# Logger para este módulo
log = get_logger("client")
# Semáforo global para limitar solicitudes simultáneas al LLM
SEM_GLOBAL = asyncio.Semaphore(settings.MAX_IN_FLIGHT)
# Generador de identificadores únicos para usuarios
USER_SEQ = itertools.count(1)  # Usuario-1, Usuario-2, ...

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Maneja la conexión de un cliente TCP.

    - Lee mensajes del cliente y envía respuestas generadas por el LLM.
    - Implementa control de tasa y concurrencia segura.
    - Registra trazabilidad detallada en logs.
    """
    # Obtener información del cliente y asignar un identificador único
    peer = writer.get_extra_info("peername")
    user = f"Usuario-{next(USER_SEQ)}"
    msg_counter = itertools.count(1)  # Contador de mensajes por conexión
    log.info(f"[{user}] Conexión desde {peer}")

    # Crear un limitador de tasa para este usuario
    limiter = SlidingWindowLimiter(
        settings.RATE_MAX_MESSAGES, settings.RATE_WINDOW_SECONDS
    )

    # Enviar mensaje de bienvenida al cliente
    greeting = (
        f"{user} conectado.\n"
        "Bienvenido a PsicoIA.\n"
        "Contame cómo te sentís hoy. Escribí 'salir' para cerrar.\n"
    )
    writer.write(greeting.encode("utf-8"))
    await writer.drain()

    try:
        while True:
            # Leer mensaje del cliente
            data = await reader.readline()
            if not data:
                break

            msg = data.decode().strip()
            if msg.lower() == "salir":
                # Cerrar la conexión si el cliente escribe 'salir'
                writer.write("Gracias por usar PsicoIA. Cuidate!\n".encode("utf-8"))
                await writer.drain()
                break

            if not limiter.allow():
                # Responder con un mensaje de límite de tasa si se excede
                writer.write(
                    "Tranca, demasiados mensajes seguidos. Probá en unos segundos.\n".encode("utf-8")
                )
                await writer.drain()
                continue

            async with SEM_GLOBAL:
                """
                Manejo de concurrencia y trazabilidad:
                - `trace_id` vincula cada solicitud al LLM con el usuario y número de mensaje.
                - Permite identificar en los logs a qué usuario corresponde cada solicitud.
                """
                trace_id = f"{user}:m{next(msg_counter)}"

                t0 = time.perf_counter()  # Marcar tiempo de inicio
                log.info(f"[{trace_id}] → LLM start (len={len(msg)})")

                # Generar respuesta del LLM usando el historial del usuario
                llm_reply = await llm_generate(msg, trace_id=trace_id, conversation_id=user)

                dt_ms = (time.perf_counter() - t0) * 1000  # Calcular latencia
                log.info(f"[{trace_id}] ← LLM ok ({len(llm_reply)} chars) {dt_ms:.0f} ms")

                # Enviar respuesta al cliente
                out = f"{llm_reply}"
                writer.write((out + "\n").encode("utf-8"))
                await writer.drain()

    except Exception as e:
        # Manejo de errores durante la conexión
        log.exception(f"[{user}] Error: {e}")
    finally:
        # Cerrar la conexión y liberar recursos
        writer.close()
        await writer.wait_closed()
        log.info(f"[{user}] Conexión cerrada")
