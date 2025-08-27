# PsicoIA (TCP)

Servidor TCP multiusuario que clasifica estado emocional y enruta a prompts/LLM.
Incluye gateway WebSocket↔TCP.

## Cómo correr
1. Copiá `.env.example` a `.env`.
2. `docker compose up -d --build`
3. TCP: `nc localhost 5001`  |  Web: abrir `web/client_web.html` (WS: `ws://localhost:8765`)
