from app.services.llm_client import llm_generate
from app.services.breathing_exercises import short_box_breathing
from app.services.resource_recommender import recommend

def classify_state(text: str) -> str:
    t = text.lower()
    if "ataque" in t or "pánico" in t or "panico" in t:
        return "aguda"
    return "moderada"

async def route_message(user_text: str) -> str:
    state = classify_state(user_text)
    prefix = "Veo señales de ansiedad aguda. Vamos paso a paso." if state == "aguda" else "Gracias por compartir cómo te sentís."
    breath = short_box_breathing()
    llm_reply = await llm_generate(user_text, state)
    recs = recommend(state)
    return f"{prefix}\n{breath}\n\n{llm_reply}\n\nRecursos: {', '.join(recs)}"
