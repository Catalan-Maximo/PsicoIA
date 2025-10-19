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

---

## Ejecutar:
### Opción A: Docker (recomendada)

Desde la raíz del proyecto (con Docker activo):

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

### Opción B: Consola/Terminal

Desde la raíz del proyecto:

```powershell
python -m app.server
#y luego en otra consola/terminal
python -m gateway.ws_gateway
```

Para detener:

```powershell
#Ctrl + C, en ambas consolas
^C
```

## Probar la aplicación

### **Opción 1: Cliente web HTML (interfaz gráfica - RECOMENDADO)**

1. Asegúrate de que `app` y `gateway` estén levantados (con Docker o localmente).
2. Abre el archivo `web/client_web.html` directamente en tu navegador (no requiere servidor web).
3. El cliente se conectará automáticamente a `ws://localhost:8765`.
4. Escribe mensajes en el chat y recibe respuestas del chatbot.
5. **Cada pestaña del navegador = usuario independiente** con su propia sesión.

---

### **Opción 2: Consola TCP directa (línea de comandos)**

Conecta directamente al servidor TCP sin pasar por el gateway WebSocket.

#### **Windows (PowerShell)**
















## 🔄 Flujo de datos y arquitectura

### **Arquitectura general**
```
┌─────────────┐     WebSocket      ┌──────────┐      TCP       ┌─────────┐      HTTP       ┌─────────┐
│  Navegador  │ ◄─────────────────► │ Gateway  │ ◄────────────► │   App   │ ◄──────────────► │   LLM   │
│ (HTML+JS)   │   ws://localhost:   │  (WS↔TCP)│   localhost:   │ (Server)│   API (Groq/   │ (Groq/  │
│             │        8765         │          │      5001      │         │    OpenAI)     │ OpenAI) │
└─────────────┘                     └──────────┘                └─────────┘                └─────────┘
     │                                   │                            │
     │                                   │                            │
     └───────────────────────────────────┴────────────────────────────┘
              Cada usuario tiene sesión aislada (1:1:1)
```

### **Flujo de un mensaje (paso a paso)**

1. **Usuario envía mensaje**:
   - Desde navegador (WebSocket) o consola TCP directa.

2. **Gateway WebSocket** (si se usa):
   - Recibe mensaje del navegador vía WebSocket.
   - Lo reenvía a través de su conexión TCP dedicada al servidor `app`.

3. **Servidor TCP (`app/server.py`)**:
   - Acepta la conexión y crea una coroutine `handle_client()`.

4. **Client Handler (`app/client_handler.py`)**:
   - Asigna ID de usuario (`Usuario-N`).
   - Valida rate limit (ventana deslizante).
   - Genera `trace_id` para trazabilidad.
   - Espera en el semáforo global (`MAX_IN_FLIGHT`).

5. **LLM Client (`app/services/llm_client.py`)**:
   - Recupera historial de conversación del usuario desde RAM.
   - Construye array de `messages` con ventana de tokens.
   - Envía POST HTTP asíncrono al LLM (Groq/OpenAI).
   - Aplica reintentos con backoff si hay errores 429/5xx.
   - Guarda respuesta en historial.

6. **Respuesta al usuario**:
   - `llm_client.py` devuelve texto al `client_handler.py`.
   - `client_handler.py` envía respuesta por TCP.
   - `gateway` (si se usa) reenvía por WebSocket al navegador.
   - El navegador o terminal muestra la respuesta.

### **Modelo de concurrencia**

- **asyncio**: Un solo proceso, un solo hilo, event loop no bloqueante.
- **Coroutines**: Cada conexión TCP obtiene su propia coroutine `handle_client()`.
- **I/O asíncrono**:
  - `await reader.readline()`: Lee sin bloquear otras conexiones.
  - `await httpx.post()`: Llama al LLM sin bloquear el servidor.
  - `await writer.drain()`: Escribe sin bloquear.
- **Protección**:
  - **Semáforo global**: Limita requests simultáneos al LLM.
  - **Rate limiter por usuario**: Previene flooding individual.

### **Gestión de estado**

- **Historial de conversación**: Almacenado en RAM en diccionario `_histories` (clave: `conversation_id`).
- **Locks por conversación**: `asyncio.Lock` evita race conditions al modificar historiales.
- **Ventana de tokens**: Solo se envían los mensajes más recientes que caben en `LLM_INPUT_TOKEN_BUDGET`.
- **Persistencia**: No hay; si reinicias el servidor, se pierden los historiales (puedes implementar DB).

---
