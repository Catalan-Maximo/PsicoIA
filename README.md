# PsicoIA (TCP)

Servidor TCP multiusuario que clasifica estado emocional y enruta a prompts/LLM.
Incluye gateway WebSocket↔TCP y MySQL + Adminer en Docker.

## Cómo correr
1. Copiá `.env.example` a `.env`.
2. `docker compose up -d --build`
3. TCP: `nc localhost 5001`  |  Web: abrir `web/client_web.html` (WS: `ws://localhost:8765`)
4. Adminer: http://localhost:3311 (server: `mysql`, user: `psicoia`, pass: `psicoia`)
