## 🎯 Objetivo del Proyecto

Desarrollar un chatbot de apoyo emocional accesible 24/7 que:
- Escuche activamente sin juzgar
- Valide emocionalmente al usuario
- Ofrezca estrategias de autocuidado
- Derive a profesionales cuando sea necesario

**⚠️ Importante**: No sustituye atención profesional de salud mental.

---

## 🏗️ Arquitectura Técnica

### Componentes principales

1. **Servidor TCP (`app/`)**
   - Puerto: 5001
   - Maneja lógica de negocio
   - Conexiones persistentes con usuarios
   - Integración con LLM

2. **Gateway WebSocket (`gateway/`)**
   - Puerto: 8765
   - Puente entre navegador y servidor TCP
   - Mapeo 1:1 de sesiones

3. **Cliente Web (`web/`)**
   - HTML/CSS/JavaScript puro
   - Interfaz moderna con tema claro/oscuro
   - Sin dependencias externas

### Flujo de datos

```
Usuario → WebSocket → Gateway → TCP → Servidor → LLM API
                                         ↓
Usuario ← WebSocket ← Gateway ← TCP ← Respuesta
```

---

## ⚙️ Características Técnicas Destacadas

### Concurrencia y escalabilidad
- **asyncio**: I/O no bloqueante, miles de usuarios simultáneos
- **Coroutines**: Una por cada conexión (sin hilos)
- **Semáforo global**: Limita requests simultáneos al LLM
- **Rate limiting**: Ventana deslizante por usuario
---

## 🔧 Stack Tecnológico

|     Componente    |        Tecnología        |          Propósito         |
|-------------------|--------------------------|----------------------------|
|   **Lenguaje**    |        Python 3.12       |       Backend completo     |
|   **Async I/O**   |          asyncio         |  Concurrencia sin threads  |
|  **HTTP Client**  |           httpx          |   Llamadas async al LLM    |
|   **WebSocket**   |        websockets        | Gateway navegador↔servidor |
| **Configuración** |     pydantic-settings    |     Validación de config   |
|    **Logging**    |     logging stdlib       |        Trazabilidad        |
|  **Contenedores** |     Docker + Compose     |          Deployment        |
|    **Frontend**   |      HTML5/CSS3/JS       |          Cliente web       |
|       **LLM**     | Groq (OpenAI compatible) |       IA conversacional    |

---

## 📁 Estructura del Código

```
PsicoIA/
├── app/                       # Servidor TCP
│   ├── server.py              # Punto de entrada
│   ├── client_handler.py      # Lógica por conexión
│   ├── config.py              # Configuración centralizada
│   ├── prompts/
│   │   └── promptgeneral.py   # Prompt del sistema
│   ├── services/
│   │   └── llm_client.py      # Cliente LLM async
│   └── utils/
│       ├── logger.py          # Logging
│       └── rate_limiter.py    # Control de tasa
├── gateway/
│   └── ws_gateway.py          # Gateway WebSocket↔TCP
├── web/
│   └── client_web.html        # Cliente navegador
├── examples/                  # Scripts de ejemplo
│   ├── tcp_client.py          # Cliente simple
│   └── async_tcp_client.py    # Pruebas de carga
├── docker-compose.yml         # Orquestación
├── Dockerfile                 # Imagen base
├── requirements.txt           # Dependencias
└── .env.example               # Template config
```












---

## 📂 Explicación detallada de cada archivo

### **Raíz del proyecto**

#### `docker-compose.yml`
- **Qué hace**: Orquesta los dos servicios principales (`app` y `gateway`) en contenedores Docker.
- **Función**: Define la configuración de red, puertos, variables de entorno y dependencias entre servicios.
- **Servicios**:
  - `app`: Servidor TCP (puerto 5001) que maneja la lógica del chatbot y conexiones al LLM.
  - `gateway`: Gateway WebSocket (puerto 8765) que actúa como puente entre navegador y servidor TCP.

#### `Dockerfile`
- **Qué hace**: Define la imagen Docker base para ambos servicios.
- **Función**: Instala Python 3.12, copia dependencias (`requirements.txt`), instala paquetes y expone los puertos 5001 y 8765.

#### `.env.example`
- **Qué hace**: Plantilla con todas las variables de entorno necesarias.
- **Variables clave**:
  - `GROQ_API_KEY`: Clave API para el proveedor LLM.
  - `MODEL_NAME`: Modelo a usar (ej: `meta-llama/llama-3.1-8b-instant`).
  - `APP_PORT`, `MAX_IN_FLIGHT`, `RATE_MAX_MESSAGES`: Configuración del servidor.
  - `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`: Parámetros del modelo.

---

### **Directorio `app/`**

#### `app/server.py`
- **Qué hace**: Punto de entrada del servidor TCP asíncrono.
- **Función**: 
  - Inicia un servidor TCP usando `asyncio.start_server()`.
  - Escucha conexiones en `APP_HOST:APP_PORT` (por defecto `0.0.0.0:5001`).
  - Por cada conexión entrante, delega el manejo a `handle_client()`.
- **Modelo de concurrencia**: 
  - Un solo proceso/hilo con asyncio (I/O no bloqueante).
  - Cada cliente obtiene su propia coroutine independiente.

#### `app/client_handler.py`
- **Qué hace**: Maneja la conexión TCP de cada cliente individual.
- **Función**:
  - Asigna un ID único por conexión (`Usuario-1`, `Usuario-2`, etc.).
  - Lee mensajes del cliente línea por línea de forma asíncrona.
  - Aplica **rate limiting** por usuario (ventana deslizante).
  - Usa un **semáforo global** (`MAX_IN_FLIGHT`) para limitar llamadas simultáneas al LLM.
  - Genera `trace_id` para trazabilidad de cada mensaje (`Usuario-X:mY`).
  - Llama a `llm_generate()` de forma asíncrona y devuelve la respuesta al cliente.
- **Aislamiento**: Cada conexión es independiente; no se mezclan estados entre usuarios.

#### `app/config.py`
- **Qué hace**: Centraliza la configuración del proyecto usando Pydantic Settings.
- **Función**:
  - Lee variables desde `.env` automáticamente.
  - Valida tipos y proporciona valores por defecto.
  - Exporta objeto `settings` usado en toda la aplicación.

---

### **Directorio `app/services/`**

#### `app/services/llm_client.py`
- **Qué hace**: Cliente asíncrono para interactuar con el LLM (Groq/OpenAI compatible).
- **Funciones principales**:
  - `llm_generate(user_text, trace_id, conversation_id)`: Envía mensaje al LLM y recibe respuesta.
  - Gestiona **historial de conversación en RAM** por usuario (`conversation_id`).
  - Implementa **ventana deslizante de tokens** para no exceder límite de contexto.
  - Aplica **reintentos con backoff exponencial** en caso de errores 429/5xx.
  - Usa `httpx.AsyncClient` para llamadas HTTP no bloqueantes.
- **Trazabilidad**: Incluye `trace_id` en headers y logs para correlacionar requests.
- **Fallback**: Si no hay API key, retorna mensaje empático offline.

---

### **Directorio `app/prompts/`**

#### `app/prompts/promptgeneral.py`
- **Qué hace**: Define el prompt del sistema para el LLM.
- **Función**:
  - Constante `SYSTEM_PROMPT` con instrucciones detalladas para el asistente psicológico.
  - Diccionario de palabras clave (alarma, ansiedad, depresión, motivación).
  - Guías de tono, estructura de respuesta y restricciones éticas.
- **Importancia**: Este archivo define la "personalidad" y comportamiento del chatbot.

---

### **Directorio `app/utils/`**

#### `app/utils/logger.py`
- **Qué hace**: Configura el sistema de logging del proyecto.
- **Función**:
  - Usa `logging.basicConfig()` con formato estándar (timestamp, nivel, mensaje).
  - Exporta `get_logger()` para obtener loggers por módulo.

#### `app/utils/rate_limiter.py`
- **Qué hace**: Implementa rate limiting por ventana deslizante.
- **Clase `SlidingWindowLimiter`**:
  - Parámetros: `max_events` (máximo mensajes), `window_seconds` (ventana temporal).
  - Método `allow()`: Retorna `True` si el usuario puede enviar mensaje, `False` si excede límite.
  - Almacena timestamps en `deque` y limpia eventos antiguos automáticamente.
- **Uso**: Previene flooding de un solo usuario sin afectar a otros.

---

### **Directorio `gateway/`**

#### `gateway/ws_gateway.py`
- **Qué hace**: Gateway WebSocket que conecta navegadores con el servidor TCP.
- **Función**:
  - Escucha conexiones WebSocket en `WS_HOST:WS_PORT` (por defecto `0.0.0.0:8765`).
  - Por **cada cliente WebSocket**, abre **una conexión TCP dedicada** al servidor `app`.
  - Mapeo **1:1** (WS ↔ TCP) garantiza aislamiento de sesiones.
  - Implementa dos coroutines asíncronas:
    - `ws_reader()`: Lee del WebSocket y escribe al TCP.
    - `tcp_reader()`: Lee del TCP y escribe al WebSocket.
- **Configuración Docker**: En compose, `TCP_HOST='app'` usa la red interna Docker.
- **Configuración local**: `TCP_HOST='127.0.0.1'` para testing sin Docker.

---







## 💡 Conceptos Clave para la Presentación

### 1. **Modelo de Concurrencia**
- "Un solo proceso Python maneja cientos de usuarios simultáneos"
- "asyncio permite I/O no bloqueante sin threads ni procesos"
- "Cada conexión es una coroutine independiente"

### 2. **Arquitectura Desacoplada**
- "Servidor TCP puro (sin web dependencies)"
- "Gateway como capa de transporte intercambiable"

### 3. **Escalabilidad Horizontal**
- "Múltiples instancias del servidor con load balancer"
- "Redis para compartir historiales entre instancias"
- "Stateless design facilita scaling"

### 4. **Gestión de Contexto LLM**
- "Ventana deslizante de tokens"
- "Solo mensajes recientes al LLM"
- "Historial completo en RAM por si se necesita"

---

## 🎤 Puntos Clave para Defender

### Decisiones de diseño

**¿Por qué asyncio en lugar de threads?**
- Más liviano: miles de coroutines vs cientos de threads
- Mejor control: event loop explícito
- Ideal para I/O-bound tasks (espera de red)

**¿Por qué separar TCP y WebSocket?**
- Separación de responsabilidades
- Testing más simple (TCP es más directo)
- Flexibilidad: agregar otros protocolos sin tocar lógica

**¿Por qué historial en RAM y no DB?**
- Prototipo funcional más rápido
- Suficiente para demo y testing
- Fácil migrar a DB después (interfaz ya definida)

**¿Por qué Docker?**
- Reproducibilidad del entorno
- Facilita deployment
- Aísla dependencias del sistema host

---