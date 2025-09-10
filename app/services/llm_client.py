"""
Asincronismo LLM:
- httpx.AsyncClient realiza la llamada HTTP sin bloquear el loop.
- Se incluye 'trace_id' en headers/logs para correlacionar cada POST con un usuario/mensaje.
- Si Groq tarda, el event loop sigue atendiendo otras conexiones (concurrencia real).
"""

import httpx
import ast
import time
import asyncio
from pathlib import Path
from collections import defaultdict
from app.config import settings
from app.utils.logger import get_logger
from app.prompts.promptgeneral import SYSTEM_PROMPT

log = get_logger("llm")

# === Memoria de conversación en RAM (no persistente) + ventana por tokens ===
_histories: dict[str, list[dict]] = defaultdict(list)
_locks: dict[str, asyncio.Lock] = {}

def _get_lock(cid: str) -> asyncio.Lock:
    lock = _locks.get(cid)
    if lock is None:
        lock = asyncio.Lock()
        _locks[cid] = lock
    return lock

async def get_history(conversation_id: str) -> list[dict]:
    async with _get_lock(conversation_id):
        return list(_histories.get(conversation_id, []))

async def append_user(conversation_id: str, text: str) -> None:
    async with _get_lock(conversation_id):
        _histories[conversation_id].append({"role": "user", "content": text})

async def append_assistant(conversation_id: str, text: str) -> None:
    async with _get_lock(conversation_id):
        _histories[conversation_id].append({"role": "assistant", "content": text})
        max_msgs = getattr(settings, "LLM_HISTORY_MAX_MESSAGES", 200)
        if len(_histories[conversation_id]) > max_msgs:
            _histories[conversation_id] = _histories[conversation_id][-max_msgs:]

async def clear_history(conversation_id: str) -> None:
    async with _get_lock(conversation_id):
        _histories.pop(conversation_id, None)

def _est_tokens_text(s: str) -> int:
    cpt = max(1, int(getattr(settings, "LLM_CHARS_PER_TOKEN", 4) or 4))
    return max(1, (len(s or "") + cpt - 1) // cpt)

def _est_tokens_msg(msg: dict) -> int:
    return _est_tokens_text(msg.get("content", "") or "")

def build_messages(system_prompt: str, history: list[dict], user_text: str) -> list[dict]:
    """Construye messages con ventana deslizante por tokens."""
    budget = int(getattr(settings, "LLM_INPUT_TOKEN_BUDGET", 2000) or 2000)
    system_msg = {"role": "system", "content": system_prompt}
    user_msg = {"role": "user", "content": user_text}

    margin = 32
    remaining = budget - _est_tokens_msg(system_msg) - _est_tokens_msg(user_msg) - margin
    remaining = max(0, remaining)

    picked: list[dict] = []
    total = 0
    for msg in reversed(history):
        t = _est_tokens_msg(msg)
        if total + t > remaining:
            break
        picked.append(msg)
        total += t
    picked.reverse()

    return [system_msg] + picked + [user_msg]

def _read_system_prompt_from_file(module_basename: str) -> str | None:
    """Read SYSTEM_PROMPT value from app/prompts/<module_basename>.py using ast.
    This avoids importing the module and therefore avoids import cache issues.
    Returns the string value or None if not found.
    """
    try:
        prompts_dir = Path(__file__).resolve().parents[1] / "prompts"
        file_path = prompts_dir / f"{module_basename}.py"
        if not file_path.exists():
            return None
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if getattr(target, "id", None) == "SYSTEM_PROMPT":
                        value = node.value
                        if isinstance(value, ast.Constant) and isinstance(value.value, str):
                            return value.value
                        # handle joined strings (e.g., f"..." or concatenation)
                        try:
                            return ast.literal_eval(value)
                        except Exception:
                            return None
        return None
    except Exception:
        return None


async def llm_generate(user_text: str, trace_id: str | None = None, conversation_id: str | None = None) -> str:
    """
    Llama a LLaMA en Groq (API OpenAI-compatible).
    Requiere GROQ_API_KEY y MODEL_NAME en el .env.
    Usa settings.LLM_URL si está definido; si no, fallback al endpoint de Groq.
    """
    api_key = getattr(settings, "GROQ_API_KEY", None)
    if not api_key:
        # Fallback offline si no hay API key
        if conversation_id:
            await append_user(conversation_id, user_text)
            await append_assistant(conversation_id, "Estoy para acompañarte. Probemos respirar suave 4-4-4-4 y contame qué sentís ahora.")
        return "Estoy para acompañarte. Probemos respirar suave 4-4-4-4 y contame qué sentís ahora."

    url = getattr(settings, "LLM_URL", None)
    model = settings.MODEL_NAME
    system_prompt = SYSTEM_PROMPT

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # Trazabilidad opcional (útil en logs/proxies)
    if trace_id:
        headers["X-Request-ID"] = trace_id

    conv_key = conversation_id
    history = await get_history(conv_key) if conv_key else []
    messages = build_messages(system_prompt, history, user_text)

    payload = {
        "model": model,
        "messages": messages,
        "temperature": settings.LLM_TEMPERATURE,
        "max_tokens": settings.LLM_MAX_TOKENS,
        "stream": False,
    }
    # Guardar el turno del usuario antes de llamar, para no perderlo si falla
    if conversation_id:
        await append_user(conversation_id, user_text)

    try:
        t0 = time.perf_counter()
        log.info(f"[{trace_id or '-'}] POST {url} model={model} len={len(user_text)}")
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            for attempt in range(1, settings.LLM_MAX_RETRIES + 1):
                resp = await client.post(url, headers=headers, json=payload)
                status = resp.status_code

                if status == 429 or 500 <= status < 600:
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait = float(retry_after)
                        except Exception:
                            wait = settings.LLM_BACKOFF_INITIAL
                    else:
                        wait = min(
                            settings.LLM_BACKOFF_MAX,
                            settings.LLM_BACKOFF_INITIAL * (2 ** (attempt - 1))
                        )
                    log.warning(f"[{trace_id or '-'}] LLM, retry {attempt}/{settings.LLM_MAX_RETRIES} in {wait:.2f}s")
                    if attempt == settings.LLM_MAX_RETRIES:
                        break
                    await asyncio.sleep(wait)
                    continue

                resp.raise_for_status()
                data = resp.json()
                content = (data.get("choices", [{}])[0]
                               .get("message", {})
                               .get("content", "")
                               .strip())
                dt_ms = (time.perf_counter() - t0) * 1000
                log.info(f"[{trace_id or '-'}] LLM OK ({len(content or '')} chars) {dt_ms:.0f} ms")
                if conversation_id:
                    await append_assistant(conversation_id, content or "")
                return content or "No recibí respuesta del modelo."

        return "Estoy recibiendo muchas solicitudes. Probemos de nuevo en unos segundos."
    except httpx.HTTPStatusError as e:
        log.error(f"[{trace_id or '-'}] Groq error: {e}")
        return "Hubo un problema con el proveedor. Intentá más tarde."
    except Exception as e:
        log.error(f"[{trace_id or '-'}] Groq error: {e}")
        return "Ocurrió un error al consultar el modelo. Intentá de nuevo."
