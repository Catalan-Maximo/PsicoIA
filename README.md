# PsicoIA — Chatbot de apoyo emocional (TCP + WebSocket)

Proyecto multiusuario basado en asyncio que expone un servidor TCP (`app`) y un gateway WebSocket (`gateway`).
Por cada cliente WebSocket el gateway abre una conexión TCP dedicada hacia la `app`, garantizando sesiones aisladas.
Las solicitudes al LLM se realizan mediante un cliente async (httpx) hacia un endpoint compatible con OpenAI (por ejemplo, Groq).

## Contenido rápido

- Servidor TCP asíncrono para múltiples usuarios (PUERTO por defecto: `5001`).
- Gateway WebSocket que actúa como puente entre navegador y servidor TCP (PUERTO por defecto: `8765`).
- Contenedores Docker y `docker compose` para desplegar localmente.

## Requisitos

- Docker Desktop o Docker Engine
- Docker Compose (incluido con Docker Desktop)
- Clave de API compatible (por ejemplo, Groq API key)
- Navegador moderno para `web/client_web.html` (opcional)

## Variables de entorno

1. Copia `.env.example` → `.env` y completa los valores.

Ejemplo clave (informativo):

```env
# App
APP_HOST=0.0.0.0
APP_PORT=5001
MAX_IN_FLIGHT=50
PER_USER_MAX=2
RATE_WINDOW_SECONDS=10
RATE_MAX_MESSAGES=6

# LLM
GROQ_API_KEY=gsk_...tu_clave...
MODEL_NAME=meta-llama/llama-3.1-8b-instant
# (Opcional) LLM_URL=https://mi-endpoint/openai/v1/chat/completions
```

2. `app/prompts/promptgeneral.py` debe definir la constante `SYSTEM_PROMPT` con el prompt del sistema.

## Estructura del repositorio (resumen)

- `app/` — servidor TCP y lógica principal
  - `server.py` — arranque del servidor TCP
  - `client_handler.py` — manejo por conexión (una coroutine por cliente)
  - `services/llm_client.py` — cliente async para LLM
  - `prompts/promptgeneral.py` — `SYSTEM_PROMPT`
  - `utils/` — logger, rate limiter, helpers
- `gateway/` — puente WebSocket ↔ TCP (`ws_gateway.py`)
- `web/` — cliente web simple (`client_web.html`)
- `Dockerfile`, `docker-compose.yml`, `requirements.txt`

## Ejecutar (recomendado: Docker)

Desde la raíz del proyecto:

```powershell
docker compose build
docker compose up -d
```

Ver servicios y puertos:

```powershell
docker compose ps
```

Ver logs:

```powershell
docker compose logs -f app
docker compose logs -f gateway
```

Detener todo:

```powershell
docker compose down
```

Reconstruir después de cambios en el código:

```powershell
docker compose up -d --build
```

## Probar la aplicación

Opción A — Cliente web (recomendado)

1. Asegúrate de que `app` y `gateway` estén levantados.
2. Abre `web/client_web.html` en tu navegador.
3. Envía mensajes; cada pestaña equivale a un usuario aislado.

Opción B — TCP directo (console)

```powershell
nc localhost 5001
# o
telnet localhost 5001
```

Escribe mensajes y observa las respuestas.

## Qué observar (demo)

- Logs de conexiones: `Usuario-1`, `Usuario-2`, …
- Llamadas al LLM con `trace_id` y latencia registrados
- Comportamiento de rate-limit si se envían demasiados mensajes seguidos

## Solución de problemas rápida

- El navegador no conecta: verifica que `gateway` publique `:8765` (usar `docker compose ps`).
- No hay respuesta del LLM: revisa `GROQ_API_KEY` y `MODEL_NAME` en `.env`.
- Puertos ocupados: cambia el mapeo en `docker-compose.yml` (ej. `5002:5001`) y reconstruye.
- Firewall: permite conexiones locales cuando Docker expone puertos.

## Notas técnicas (resumen)

- Concurrencia: `asyncio.start_server()` crea una coroutine por cliente; I/O no bloqueante.
- Aislamiento: cada WebSocket abre una conexión TCP 1:1 con `app`.
- LLM: `httpx.AsyncClient` para llamadas async al modelo compatible OpenAI/Groq.
- Seguridad/operaciones: añade control de errores, límites y trazabilidad via `trace_id`.

---
