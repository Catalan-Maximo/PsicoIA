import httpx
from app.config import settings

# Endpoint OpenAI-compatible de Groq
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

PROMPTS = {
    "moderada": "Sos un asistente empático. Respondé breve y proponé un siguiente paso.",
    "aguda": "Sos un asistente muy calmado. Guiá respiración y anclaje, frases cortas y claras.",
}

async def llm_generate(user_text: str, state: str) -> str:
    """
    Llama a LLaMA en Groq usando la API OpenAI-compatible.
    Requiere GROQ_API_KEY y MODEL_NAME en el .env
    """
    api_key = settings.OPENAI_API_KEY or None  # compat si alguien dejó OPENAI_API_KEY
    # Preferimos GROQ_API_KEY explícito:
    api_key = getattr(settings, "GROQ_API_KEY", None) or api_key

    if not api_key:
        # Fallback offline si no hay API key
        return "Estoy para acompañarte. Probemos respirar suave 4-4-4-4 y contame qué sentís ahora."

    model = settings.MODEL_NAME or "meta-llama/llama-3.1-8b-instant"
    system_prompt = PROMPTS.get(state, PROMPTS["moderada"])

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
        "temperature": 0.2,
        "max_tokens": 200,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(GROQ_CHAT_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # Respuesta OpenAI-like
            return (data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip()) or "No recibí respuesta del modelo."
    except Exception as e:
        return f"(Error al consultar Groq: {e})"
