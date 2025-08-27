import httpx
import ast
from pathlib import Path
from app.config import settings

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


def _load_prompt_for_state(state: str) -> str | None:
    """Load prompt by reading the prompt file from disk.
    Uses ast parsing to avoid module caching. Returns the prompt string or None
    if the file/constant is not present.
    """
    # Using the general prompt file 'promptgeneral.py' by default.
    module_basename = "promptgeneral"
    return _read_system_prompt_from_file(module_basename)


async def llm_generate(user_text: str, state: str) -> str:
    """
    Llama a LLaMA en Groq usando la API OpenAI-compatible.
    Requiere GROQ_API_KEY y MODEL_NAME en el .env
    """
    api_key = getattr(settings, "GROQ_API_KEY", None) or "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"

    if not api_key:
        # Fallback offline si no hay API key
        return "Estoy para acompañarte. Probemos respirar suave 4-4-4-4 y contame qué sentís ahora."

    model = settings.MODEL_NAME or "llama3-70b-8192"
    system_prompt = _load_prompt_for_state(state)
    if not system_prompt:
        return "(No SYSTEM_PROMPT found — create app/prompts/promptgeneral.py with SYSTEM_PROMPT)"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.7,
        "max_tokens": 400,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(settings.LLM_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # Respuesta OpenAI-like
            return (data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip()) or "No recibí respuesta del modelo."
    except Exception as e:
        return f"(Error al consultar Groq: {e})"
