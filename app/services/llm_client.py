"""
Módulo para comunicar con un LLM remoto (Groq/OpenAI-compatible).

- Gestiona la memoria de conversación en RAM, con soporte para múltiples sesiones.
- Implementa mecanismos de concurrencia seguros usando asyncio.Lock.
- Proporciona funciones para construir mensajes y realizar llamadas al LLM.
"""

# --- Variables globales ---
# _histories: Almacena el historial de mensajes por conversación.
# _locks: Gestiona un asyncio.Lock por conversación para acceso seguro.
_histories: dict[str, list[dict]] = defaultdict(list)
_locks: dict[str, asyncio.Lock] = {}

def _get_lock(cid: str) -> asyncio.Lock:
    """
    Obtener (o crear) un lock exclusivo para la conversación `cid`.

    - Evita condiciones de carrera en acceso a `_histories[cid]`.
    - Si no hay lock creado, se crea y se guarda en `_locks`.
    """
    # Buscar lock existente
    lock = _locks.get(cid)
    # Si no existe, crear uno y almacenarlo
    if lock is None:
        lock = asyncio.Lock()
        _locks[cid] = lock
    # Devolver el lock (siempre un asyncio.Lock)
    return lock

async def get_history(conversation_id: str) -> list[dict]:
    """
    Devuelve la historia completa de `conversation_id` de forma segura.

    - Usa el lock asociado para operaciones concurrentes.
    - Devuelve una copia (`list(...)`) para que el llamador no mutile
      la estructura interna compartida.
    """
    # Adquirir lock para lectura segura
    async with _get_lock(conversation_id):
        # Retornar una copia de la lista de mensajes (puede ser vacía)
        return list(_histories.get(conversation_id, []))

async def append_user(conversation_id: str, text: str) -> None:
    """
    Añade un mensaje del usuario a la conversación en memoria.

    - Guarda un diccionario con keys `role` y `content`.
    - Protegido con lock para concurrencia.
    """
    # Bloquear la conversación mientras se muta la lista
    async with _get_lock(conversation_id):
        _histories[conversation_id].append({"role": "user", "content": text})

async def append_assistant(conversation_id: str, text: str) -> None:
    """
    Añade un mensaje del asistente y mantiene la longitud máxima.

    - Si la lista excede `LLM_HISTORY_MAX_MESSAGES`, recorta los mensajes
      más antiguos para mantener sólo los últimos `max_msgs`.
    """
    async with _get_lock(conversation_id):
        # Añadir mensaje del asistente
        _histories[conversation_id].append({"role": "assistant", "content": text})
        # Número máximo de mensajes a almacenar (configurable)
        max_msgs = getattr(settings, "LLM_HISTORY_MAX_MESSAGES", 200)
        # Si excede, mantener sólo los últimos `max_msgs`
        if len(_histories[conversation_id]) > max_msgs:
            _histories[conversation_id] = _histories[conversation_id][-max_msgs:]

async def clear_history(conversation_id: str) -> None:
    """
    Borrar la historia completa de `conversation_id`.

    - Útil para reiniciar el contexto de una sesión.
    """
    async with _get_lock(conversation_id):
        _histories.pop(conversation_id, None)

def _est_tokens_text(s: str) -> int:
    """
    Estima el número de tokens para un texto `s` usando una regla simple.

    - Usa `LLM_CHARS_PER_TOKEN` para dividir caracteres->tokens.
    - No pretende reemplazar un tokenizador real, sólo sirve para control
      del presupuesto de entrada.
    """
    # Chars per token (configurable), por seguridad al menos 1
    cpt = max(1, int(getattr(settings, "LLM_CHARS_PER_TOKEN", 4) or 4))
    # Redondeo hacia arriba de len(s)/cpt
    return max(1, (len(s or "") + cpt - 1) // cpt)

def _est_tokens_msg(msg: dict) -> int:
    """
    Estima tokens del campo `content` de `msg`.

    - `msg` se espera con key `content` que contiene el texto.
    """
    return _est_tokens_text(msg.get("content", "") or "")

def build_messages(system_prompt: str, history: list[dict], user_text: str) -> list[dict]:
    """
    Construye la lista `messages` que se enviará al modelo.

    - Incluye un `system` al inicio, preserva tantos mensajes previos como
      quepan en el presupuesto de tokens (`LLM_INPUT_TOKEN_BUDGET`), y
      finalmente añade el mensaje del usuario.
    - La ventana es deslizante: se recogen mensajes desde el final hacia atrás
      hasta llenar el presupuesto estimado.
    """
    # Presupuesto total de tokens para el input (configurable)
    budget = int(getattr(settings, "LLM_INPUT_TOKEN_BUDGET", 2000) or 2000)
    # Mensajes fijo: system al inicio y user al final
    system_msg = {"role": "system", "content": system_prompt}
    user_msg = {"role": "user", "content": user_text}

    # Dejamos un pequeño margen de tokens para seguridad/overhead
    margin = 32
    # Calcular tokens restantes después de system + user + margin
    remaining = budget - _est_tokens_msg(system_msg) - _est_tokens_msg(user_msg) - margin
    remaining = max(0, remaining)

    # Recorrer la historia desde el final (más reciente) hacia atrás
    # y recoger mensajes hasta llenar el presupuesto `remaining`.
    picked: list[dict] = []
    total = 0
    for msg in reversed(history):
        t = _est_tokens_msg(msg)  # tokens estimados de este mensaje
        if total + t > remaining:
            # Si añadir este mensaje excede el presupuesto, parar
            break
        picked.append(msg)
        total += t
    # Volver a orden original (más antiguo -> más nuevo)
    picked.reverse()

    # Devolver la secuencia completa: system + context escogido + user
    return [system_msg] + picked + [user_msg]

def _read_system_prompt_from_file(module_basename: str) -> str | None:
    """
    Lee el valor de SYSTEM_PROMPT desde un archivo en `app/prompts` usando ast.

    - Evita importar el módulo directamente para prevenir efectos secundarios.
    - Devuelve el valor de la constante o None si no se encuentra.
    """
    try:
        # Directorio `app/prompts`
        prompts_dir = Path(__file__).resolve().parents[1] / "prompts"
        file_path = prompts_dir / f"{module_basename}.py"
        # Si no existe el archivo, no hay prompt personalizado
        if not file_path.exists():
            return None
        # Leer el contenido del archivo y parsearlo con ast
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
        # Buscar asignaciones top-level cuyo target sea `SYSTEM_PROMPT`
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if getattr(target, "id", None) == "SYSTEM_PROMPT":
                        value = node.value
                        # Si es una constante string simple
                        if isinstance(value, ast.Constant) and isinstance(value.value, str):
                            return value.value
                        # Intentar evaluar literales compuestas (concatenaciones)
                        try:
                            return ast.literal_eval(value)
                        except Exception:
                            return None
        # Si no encontramos la variable, devolver None
        return None
    except Exception:
        # En caso de error de parseo o I/O, devolver None silenciosamente
        return None

async def llm_generate(user_text: str, trace_id: str | None = None, conversation_id: str | None = None) -> str:
    """
    Llama a LLaMA en Groq (API OpenAI-compatible).

    - Requiere GROQ_API_KEY y MODEL_NAME en el .env.
    - Usa settings.LLM_URL si está definido; si no, fallback al endpoint de Groq.
    """
    # Obtener credenciales; si no hay API key, usamos una respuesta por defecto
    api_key = getattr(settings, "GROQ_API_KEY", None)
    # Si no está configurada la API key, devolvemos una respuesta local
    if not api_key:
        # Guardar el turno del usuario y la respuesta simulada en la historia
        if conversation_id:
            await append_user(conversation_id, user_text)
            await append_assistant(conversation_id, "Estoy para acompañarte. Probemos respirar suave 4-4-4-4 y contame qué sentís ahora.")
        # Respuesta por defecto en modo offline
        return "Estoy para acompañarte. Probemos respirar suave 4-4-4-4 y contame qué sentís ahora."

    url = getattr(settings, "LLM_URL", None)
    model = settings.MODEL_NAME
    system_prompt = SYSTEM_PROMPT

    # Construir headers para la API compatible con OpenAI (Groq)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # Si se pasó un trace_id, añadirlo para trazabilidad en logs/proxies
    if trace_id:
        headers["X-Request-ID"] = trace_id

    # Recuperar la historia asociada a la conversación (si hay)
    conv_key = conversation_id
    history = await get_history(conv_key) if conv_key else []
    # Construir la lista `messages` (system + contexto + user)
    messages = build_messages(system_prompt, history, user_text)

    # Payload para la API: modelo, mensajes y parámetros de generación
    payload = {
        "model": model,
        "messages": messages,
        "temperature": settings.LLM_TEMPERATURE,
        "max_tokens": settings.LLM_MAX_TOKENS,
        "stream": False,
    }
    # Guardar el turno del usuario en la historia antes de la llamada
    # para no perder el registro en caso de fallo de red/proveedor.
    if conversation_id:
        await append_user(conversation_id, user_text)

    try:
        # Marcar tiempo de inicio para métricas
        t0 = time.perf_counter()
        log.info(f"[{trace_id or '-'}] POST {url} model={model} len={len(user_text)}")

        # Realizar la petición HTTP con reintentos (httpx.AsyncClient)
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            for attempt in range(1, settings.LLM_MAX_RETRIES + 1):
                # Enviar POST al endpoint configurado
                resp = await client.post(url, headers=headers, json=payload)
                status = resp.status_code

                # Manejo de errores transitorios: 429 (rate-limit) y 5xx
                if status == 429 or 500 <= status < 600:
                    # Intentar respetar header Retry-After si viene
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait = float(retry_after)
                        except Exception:
                            wait = settings.LLM_BACKOFF_INITIAL
                    else:
                        # Backoff exponencial con límite superior
                        wait = min(
                            settings.LLM_BACKOFF_MAX,
                            settings.LLM_BACKOFF_INITIAL * (2 ** (attempt - 1))
                        )
                    log.warning(f"[{trace_id or '-'}] LLM, retry {attempt}/{settings.LLM_MAX_RETRIES} in {wait:.2f}s")
                    if attempt == settings.LLM_MAX_RETRIES:
                        # Si es el último intento, romper y devolver mensaje amigable
                        break
                    # Esperar antes de reintentar
                    await asyncio.sleep(wait)
                    continue

                # Si el código no fue transitorio, forzar raise_for_status
                resp.raise_for_status()
                # Parsear JSON de la respuesta
                data = resp.json()

                # Extraer el contenido en formato OpenAI-compatible
                content = (data.get("choices", [{}])[0]
                               .get("message", {})
                               .get("content", "")
                               .strip())

                # Registrar tiempo total de respuesta
                dt_ms = (time.perf_counter() - t0) * 1000
                log.info(f"[{trace_id or '-'}] LLM OK ({len(content or '')} chars) {dt_ms:.0f} ms")

                # Guardar respuesta del asistente en la historia si corresponde
                if conversation_id:
                    await append_assistant(conversation_id, content or "")
                # Devolver contenido (o mensaje por defecto si está vacío)
                return content or "No recibí respuesta del modelo."

        # Si agotamos reintentos sin una respuesta válida
        return "Estoy recibiendo muchas solicitudes. Probemos de nuevo en unos segundos."
    except httpx.HTTPStatusError as e:
        # Errores HTTP manejados aquí
        log.error(f"[{trace_id or '-'}] Groq error: {e}")
        return "Hubo un problema con el proveedor. Intentá más tarde."
    except Exception as e:
        # Otros errores (timeout, parseo, etc.)
        log.error(f"[{trace_id or '-'}] Groq error: {e}")
        return "Ocurrió un error al consultar el modelo. Intentá de nuevo."
