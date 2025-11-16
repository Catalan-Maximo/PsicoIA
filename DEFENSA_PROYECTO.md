## Descripción General del Proyecto

**PsicoIA** es un sistema de chatbot de apoyo emocional basado en arquitectura cliente-servidor que utiliza **TCP** como protocolo de comunicación. El sistema está diseñado para ser **multiusuario**, **concurrente** y **escalable**, permitiendo que múltiples usuarios se conecten simultáneamente y reciban acompañamiento emocional personalizado.

---

## ✅ Operaciones Admitidas

El sistema implementa las siguientes características funcionales:

1. ✅ **Conversaciones simultáneas** entre múltiples usuarios con estado de sesión aislado
2. ✅ **Limitación de velocidad por usuario** (ventana deslizante y número de mensajes configurables)
3. ✅ **Control global de contrapresión** (número máximo de solicitudes LLM simultáneas configurables mediante semáforo)
4. ✅ **Reintento automático con backoff exponencial** para fallos transitorios de la API
5. ✅ **Ajuste de ventana de tokens** para adaptar el historial de conversación a los límites del contexto del modelo
6. ✅ **Degradación controlada** cuando la API de LLM no está disponible (respuesta de fallback)
7. ✅ **Opciones de conectividad duales**: WebSocket (navegadores) y TCP directo (clientes nativos)
8. ✅ **Generación de trace_id** para depuración de solicitudes en todos los componentes
9. ✅ **Observabilidad completa** con logs estructurados y métricas de latencia
10. ✅ **Containerización** con Docker para reproducibilidad y despliegue simple

---

## ⚠️ Limitaciones Conocidas

El sistema tiene las siguientes limitaciones por diseño (prototipo educativo):

1. ⚠️ **Historial en RAM**: Las conversaciones se pierden al reiniciar el servidor
2. ⚠️ **Sin autenticación**: No hay sistema de cuentas de usuario ni control de acceso
3. ⚠️ **Sin persistencia**: No se guardan conversaciones en base de datos
4. ⚠️ **Instancia única**: Despliegue monolítico sin escalado horizontal (requeriría estado externo compartido)
5. ⚠️ **Sin cifrado TLS/SSL**: Las comunicaciones no están cifradas (HTTP/WS plano)
6. ⚠️ **Identificación temporal**: `Usuario-N` es secuencial y no persistente entre sesiones
7. ⚠️ **Sin recuperación de sesión**: Si un cliente se desconecta, pierde su historial

**Nota**: Estas limitaciones son intencionales para mantener la simplicidad del prototipo educativo. Todas son resolubles con las extensiones mencionadas en la pregunta 12 ("¿Cómo escalaría el sistema para producción?").

---

### Objetivos del Proyecto

1. **Proporcionar apoyo emocional inmediato** mediante un chatbot inteligente
2. **Demostrar arquitectura de red robusta** con TCP y WebSocket
3. **Implementar concurrencia real** usando programación asíncrona
4. **Garantizar observabilidad** con sistema de logs y trazabilidad
5. **Facilitar el despliegue** mediante contenedores Docker

### Características Principales

- ✅ **Servidor TCP Multiusuario**: Soporta múltiples conexiones simultáneas
- ✅ **Gateway WebSocket**: Permite que navegadores web se conecten al servidor TCP
- ✅ **Concurrencia Asíncrona**: Uso de `asyncio` para manejar miles de conexiones
- ✅ **Integración con LLM**: Utiliza modelos de lenguaje (Groq/LLaMA) para respuestas inteligentes
- ✅ **Rate Limiting**: Protección contra flooding por usuario
- ✅ **Historial Conversacional**: Mantiene contexto de la conversación
- ✅ **Containerización**: Deploy simple con Docker Compose
- ✅ **Cliente Web Moderno**: Interface HTML/JS con diseño empático

---

## Arquitectura del Sistema

### Diagrama de Componentes

```
┌─────────────────┐
│   Navegador     │
│  (Cliente Web)  │
└────────┬────────┘
         │ WebSocket (ws://localhost:8765)
         │
┌────────▼────────┐
│  Gateway WS     │
│   (Puerto 8765) │ ◄── Traduce WebSocket ↔ TCP
└────────┬────────┘
         │ TCP (localhost:5001)
         │
┌────────▼────────┐
│  Servidor TCP   │
│   (Puerto 5001) │ ◄── Maneja múltiples clientes
└────────┬────────┘
         │
         ├──► cliente_handler (coroutine por cliente)
         │
         ├──► llm_client (llamadas a API externa)
         │
         └──► rate_limiter (control de flooding)
```

### Flujo de Datos

1. **Usuario en navegador** → escribe mensaje
2. **Cliente Web HTML/JS** → envía por WebSocket al gateway
3. **Gateway WS** → traduce y reenvía por TCP al servidor
4. **Servidor TCP** → recibe, procesa y asigna al cliente_handler
5. **Client Handler** → valida rate limit, mantiene historial
6. **LLM Client** → envía prompt a modelo de IA (Groq)
7. **Respuesta del LLM** → vuelve por el camino inverso
8. **Usuario ve respuesta** en su navegador

---

## Estructura del Proyecto

```
PsicoIA/
│
├── app/                          # Núcleo del servidor TCP
│   ├── __init__.py
│   ├── server.py                 # Punto de entrada del servidor TCP
│   ├── client_handler.py         # Maneja cada cliente individual
│   ├── config.py                 # Configuración (variables de entorno)
│   │
│   ├── services/
│   │   ├── llm_client.py         # Cliente para LLM (Groq/LLaMA)
│   │
│   ├── utils/
│   │   ├── logger.py             # Sistema de logging
│   │   ├── rate_limiter.py       # Control de tasa por usuario
│   │
│   └── prompts/
│       ├── promptgeneral.py      # Prompt del sistema para el LLM
│
├── gateway/                      # Gateway WebSocket ↔ TCP
│   ├── __init__.py
│   └── ws_gateway.py             # Servidor WebSocket
│
├── web/
│   └── client_web.html           # Cliente web (HTML + JS + CSS)
│
├── docker-compose.yml            # Orquestación de contenedores
├── Dockerfile                    # Imagen del contenedor
├── requirements.txt              # Dependencias Python
├── .env                          # Variables de entorno (no en repo)
└── README.md                     # Documentación principal
```

### Responsabilidades de Cada Módulo

| Módulo | Responsabilidad |
|--------|-----------------|
| `server.py` | Inicializa el servidor TCP y acepta conexiones |
| `client_handler.py` | Maneja el ciclo de vida de cada cliente conectado |
| `llm_client.py` | Se comunica con la API del modelo de lenguaje |
| `rate_limiter.py` | Implementa ventana deslizante para rate limiting |
| `ws_gateway.py` | Traduce entre WebSocket y TCP |
| `client_web.html` | Interface de usuario en el navegador |
| `config.py` | Centraliza configuración usando `pydantic-settings` |

---

## Funcionamiento Paso a Paso

### 1. Inicio del Servidor

```python
# app/server.py
async def main():
    server = await asyncio.start_server(
        handle_client,         # Callback para cada cliente
        host=settings.APP_HOST,
        port=settings.APP_PORT,
    )
    async with server:
        await server.serve_forever()
```

**¿Qué ocurre aquí?**
- Se crea un **socket de escucha** TCP en el puerto 5001
- El socket se configura como **no bloqueante**
- Por cada conexión entrante, `asyncio` **agenda automáticamente** una nueva coroutine `handle_client()`
- El servidor queda en un loop infinito esperando conexiones

### 2. Llegada de un Cliente

```python
# app/client_handler.py
async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")  # IP y puerto del cliente
    user = f"Usuario-{next(USER_SEQ)}"        # Etiqueta única
    
    # Saludo inicial
    greeting = f"{user} conectado.\nBienvenido a PsicoIA.\n..."
    writer.write(greeting.encode("utf-8"))
    await writer.drain()
```

**¿Qué ocurre aquí?**
- Se obtiene la información del cliente (IP, puerto)
- Se asigna un **identificador único** (`Usuario-1`, `Usuario-2`, etc.)
- Se crea un **rate limiter exclusivo** para este cliente
- Se envía un mensaje de bienvenida

### 3. Procesamiento de Mensajes

```python
while True:
    data = await reader.readline()  # Lee hasta \n, NO BLOQUEA
    if not data:
        break  # Cliente desconectado
    
    msg = data.decode().strip()
    
    # Verificar rate limit
    if not limiter.allow():
        writer.write("Demasiados mensajes...\n".encode("utf-8"))
        await writer.drain()
        continue
    
    # Semáforo global para limitar concurrencia
    async with SEM_GLOBAL:
        trace_id = f"{user}:m{next(msg_counter)}"
        
        # Llamada asíncrona al LLM
        llm_reply = await llm_generate(msg, trace_id=trace_id, conversation_id=user)
        
        # Enviar respuesta al cliente
        writer.write((llm_reply + "\n").encode("utf-8"))
        await writer.drain()
```

**¿Qué ocurre aquí?**
1. **Lectura asíncrona**: `await reader.readline()` espera datos sin bloquear otros clientes
2. **Rate limiting**: Verifica que el usuario no esté enviando demasiados mensajes
3. **Semáforo global**: Limita cuántas llamadas simultáneas al LLM pueden haber
4. **Trazabilidad**: Cada request tiene un `trace_id` único (ej: `Usuario-3:m5`)
5. **Llamada al LLM**: Se envía el mensaje al modelo de lenguaje
6. **Respuesta**: Se escribe de vuelta al socket del cliente

### 4. Integración con el LLM

```python
# app/services/llm_client.py
async def llm_generate(user_text: str, trace_id: str, conversation_id: str):
    # Recuperar historial de la conversación
    history = await get_history(conversation_id)
    
    # Construir contexto con ventana deslizante
    messages = build_messages(SYSTEM_PROMPT, history, user_text)
    
    # Guardar turno del usuario
    await append_user(conversation_id, user_text)
    
    # Llamada HTTP asíncrona a Groq
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=payload)
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
    
    # Guardar respuesta del asistente
    await append_assistant(conversation_id, content)
    
    return content
```

**¿Qué ocurre aquí?**
1. **Recuperación de historial**: Obtiene mensajes previos de este usuario
2. **Construcción del prompt**: Incluye contexto relevante dentro del presupuesto de tokens
3. **Llamada HTTP asíncrona**: Usa `httpx.AsyncClient` para no bloquear
4. **Persistencia en RAM**: Guarda el intercambio en memoria para futuras referencias

### 5. Gateway WebSocket ↔ TCP

```python
# gateway/ws_gateway.py
async def bridge_ws_to_tcp(websocket):
    # Abrir conexión TCP al servidor
    reader, writer = await asyncio.open_connection(TCP_HOST, TCP_PORT)
    
    async def ws_reader():
        # Lee del WebSocket y escribe al TCP
        async for message in websocket:
            writer.write((message.strip() + "\n").encode("utf-8"))
            await writer.drain()
    
    async def tcp_reader():
        # Lee del TCP y escribe al WebSocket
        while not reader.at_eof():
            line = await reader.readline()
            if not line:
                break
            await websocket.send(line.decode("utf-8"))
    
    # Ejecutar ambas tareas en paralelo
    await asyncio.gather(ws_reader(), tcp_reader())
```

**¿Qué ocurre aquí?**
1. Por cada conexión WebSocket, se abre **una conexión TCP propia** al servidor
2. Se crean **dos tareas asíncronas** que corren en paralelo:
   - Una lee del WebSocket y escribe al TCP
   - Otra lee del TCP y escribe al WebSocket
3. Esto crea un **puente bidireccional** transparente
4. Cuando cualquiera de las dos conexiones se cierra, ambas se terminan

---

## Conceptos Técnicos Fundamentales

### 🔌 ¿Qué es un Socket?

Un **socket** es un punto final de comunicación entre dos programas a través de una red. Piensa en él como un "enchufe virtual" donde se conectan dos aplicaciones para intercambiar datos.

**Analogía**: Es como un número de teléfono. El servidor tiene un número (IP + puerto) y "atiende llamadas" de clientes que quieren comunicarse.

#### En el Código

```python
# El servidor crea un socket de escucha
server = await asyncio.start_server(
    handle_client,
    host="0.0.0.0",  # Escucha en todas las interfaces
    port=5001        # Puerto TCP
)

# Para cada cliente, asyncio crea automáticamente:
# - reader: StreamReader (para leer del socket)
# - writer: StreamWriter (para escribir al socket)
```

**¿Dónde está en nuestro proyecto?**
- `app/server.py`: Crea el socket de escucha
- `app/client_handler.py`: Usa `reader` y `writer` para cada cliente
- `gateway/ws_gateway.py`: Abre sockets TCP hacia el servidor

### 🌐 ¿Qué es TCP?

**TCP (Transmission Control Protocol)** es un protocolo de comunicación que garantiza:

1. **Confiabilidad**: Los datos llegan o se notifica el error
2. **Orden**: Los mensajes llegan en el orden enviado
3. **Control de flujo**: No se sobrecarga al receptor
4. **Detección de errores**: Checksums para validar integridad

#### ¿Por qué los mensajes llegan en orden?

TCP implementa **números de secuencia**:
- Cada byte enviado tiene un número único
- El receptor reordena paquetes si llegan desordenados
- Reconoce la recepción con ACKs (acknowledgments)
- Retransmite paquetes perdidos

```
Cliente envía:  [Paq1: "Hola"] [Paq2: " mundo"]
Red desordena:  [Paq2] llega primero
TCP reordena:   [Paq1] [Paq2]
App recibe:     "Hola mundo"  ← ¡En orden!
```

**Ventaja para nuestro proyecto**: No necesitamos preocuparnos por reordenamiento de mensajes. TCP lo maneja automáticamente.

### 🔄 ¿Qué es Asincronismo?

**Asincronismo** es un paradigma de programación donde las operaciones que tardan (I/O de red, disco, etc.) **no bloquean** la ejecución del programa.

#### Comparación: Síncrono vs Asíncrono

**Código Síncrono (Bloqueante)**:
```python
data = socket.read()  # ⏸️ Bloquea hasta que lleguen datos
# No puede hacer nada más mientras espera
process(data)
```

**Código Asíncrono (No Bloqueante)**:
```python
data = await reader.readline()  # 🏃 Cede el control mientras espera
# El event loop puede atender otras conexiones
process(data)
```

#### Event Loop

El **event loop** es el corazón de `asyncio`. Es un bucle que:
1. Revisa qué tareas están esperando I/O
2. Ejecuta las que tienen datos disponibles
3. Registra callbacks para las que todavía esperan
4. Vuelve a empezar

```python
# Visualización conceptual del event loop
while True:
    tareas_listas = obtener_tareas_con_datos_disponibles()
    for tarea in tareas_listas:
        ejecutar_hasta_proximo_await(tarea)
    
    registrar_callbacks_para_IO_pendiente()
    esperar_eventos_IO_del_OS()
```

**En nuestro proyecto**:
```python
# Múltiples clientes pueden estar en diferentes estados
Cliente 1: await reader.readline()     # Esperando entrada
Cliente 2: await llm_generate(...)     # Esperando respuesta del LLM
Cliente 3: await writer.drain()        # Esperando que se envíen datos

# El event loop alterna entre ellos eficientemente
```

### 🧵 ¿Qué es un Hilo (Thread)?

Un **hilo** es una unidad de ejecución dentro de un proceso. Permite ejecutar múltiples flujos de código "simultáneamente" (en realidad se turnan muy rápido).

**Problema con hilos**:
- Cada hilo consume ~8MB de RAM (stack)
- Context switch (cambio de hilo) es costoso
- Sincronización compleja (locks, race conditions)

```python
# Ejemplo con hilos (NO usado en nuestro proyecto)
import threading

def handle_client(socket):
    # Maneja un cliente
    pass

for connection in connections:
    thread = threading.Thread(target=handle_client, args=(connection,))
    thread.start()

# Con 1000 clientes = 1000 hilos = ~8GB RAM solo en stacks
```

### ⚡ ¿Qué es Concurrencia?

**Concurrencia** es la capacidad de manejar múltiples tareas progresando al mismo tiempo (aunque no necesariamente ejecutándose en el mismo instante).

**No es lo mismo que paralelismo**:
- **Concurrencia**: Dos tareas progresan intercalándose (un solo núcleo CPU)
- **Paralelismo**: Dos tareas ejecutándose realmente al mismo tiempo (múltiples núcleos CPU)

**Nuestro proyecto usa concurrencia cooperativa**:
```python
# Múltiples clientes comparten un solo hilo
async def handle_client(reader, writer):
    while True:
        data = await reader.readline()  # Cede control aquí
        # Cuando hay datos, retoma desde aquí
        response = await llm_generate(data)  # Cede control aquí
        await writer.drain()  # Cede control aquí
```

### 🚦 Nivel de Concurrencia

El **nivel de concurrencia** determina cuántas operaciones simultáneas permite el sistema.

**En nuestro proyecto**:

1. **Conexiones simultáneas**: Ilimitadas (limitado solo por recursos del SO)
   ```python
   # Cada cliente tiene su propia coroutine
   server = await asyncio.start_server(handle_client, ...)
   ```

2. **Llamadas simultáneas al LLM**: Limitadas por semáforo
   ```python
   SEM_GLOBAL = asyncio.Semaphore(settings.MAX_IN_FLIGHT)
   
   async with SEM_GLOBAL:  # Solo N pueden entrar aquí simultáneamente
       llm_reply = await llm_generate(...)
   ```

3. **Mensajes por usuario**: Limitados por rate limiter
   ```python
   limiter = SlidingWindowLimiter(max_messages=10, window_seconds=60)
   if not limiter.allow():
       return "Demasiados mensajes"
   ```

**Control de flujo**:
```
┌────────────┐
│ 1000 clientes conectados │
└──────┬─────┘
       │
       ├──► 995 esperando datos (await readline)
       │
       ├──► 3 esperando respuesta LLM (await llm_generate)
       │           │
       │           ├─► Solo 2 en vuelo (SEM_GLOBAL = 2)
       │           └─► 1 esperando en semáforo
       │
       └──► 2 enviando respuesta (await drain)
```

### 🔍 ¿Cómo Identificamos Usuarios?

**Estrategia de identificación**:
1. **Contador secuencial**: `Usuario-1`, `Usuario-2`, etc.
2. **Por conexión**: Cada socket TCP es único
3. **Historial por conversation_id**: Se usa el identificador del usuario como clave

```python
# En client_handler.py
USER_SEQ = itertools.count(1)  # Contador global atómico

async def handle_client(reader, writer):
    user = f"Usuario-{next(USER_SEQ)}"  # Atómico por naturaleza de asyncio
    
    # Cada cliente tiene su propio:
    # - Socket (reader/writer)
    # - Rate limiter
    # - Contador de mensajes
    # - Historial conversacional
```

**Aislamiento de estado**:
```python
# Historial en RAM por conversation_id
_histories: dict[str, list[dict]] = defaultdict(list)

# "Usuario-1" → [{"role": "user", "content": "Hola"}, ...]
# "Usuario-2" → [{"role": "user", "content": "Ayuda"}, ...]
# No se mezclan porque cada uno tiene su clave única
```

---

## Decisiones Tecnológicas y Justificaciones

### ✅ Por qué AsyncIO en vez de Threading

| Aspecto | Threading | AsyncIO |
|---------|-----------|---------|
| **Escalabilidad** | ~100-1000 hilos | ~10,000-100,000 coroutines |
| **Memoria** | 8MB por hilo | ~1KB por coroutine |
| **Context switch** | Costoso (kernel) | Barato (user space) |
| **Sincronización** | Locks, mutexes | Naturalmente cooperativo |
| **Ideal para** | CPU-bound | I/O-bound (nuestro caso) |
| **GIL** | Contención del GIL | Sin problema (un solo thread) |

#### Razones Clave:

**1. Menor sobrecarga (Overhead)**
```python
# Threading: 1000 clientes = 1000 hilos
# - 8MB × 1000 = 8GB RAM solo en stacks
# - Context switches constantes (kernel space)
# - Contención del GIL de Python

# AsyncIO: 1000 clientes = 1000 coroutines
# - ~1KB × 1000 = ~10MB RAM (coroutines + buffers)
# - Context switches cooperativos (user space)
# - Sin GIL (un solo thread, no hay competencia)
```

**2. Mejor control con Event Loop explícito**
```python
# Con threading: el SO decide cuándo cambiar de hilo (preemptivo)
# Con asyncio: el código decide cuándo ceder control (cooperativo)

async def handle_client(reader, writer):
    data = await reader.readline()  # Cede control aquí
    # Solo retoma cuando hay datos disponibles
    response = await llm_generate(data)  # Cede control aquí
    await writer.drain()  # Cede control aquí
```

**3. Ideal para I/O-bound (operaciones de red)**
```python
# Nuestro tiempo de procesamiento:
# ┌─────────────────────────────────┐
# │ Esperando I/O (red): 95%        │████████████████████
# │ Procesando CPU: 5%              │█
# └─────────────────────────────────┘

# Threading sería desperdicio:
# - Hilos esperan bloqueados (no hacen nada útil)
# - Overhead de sincronización para casi nada de CPU

# AsyncIO es perfecto:
# - Cuando un cliente espera I/O, otro progresa
# - CPU siempre ocupada con trabajo útil
# - Sin overhead de cambio de contexto del kernel
```

**4. Sin contención del GIL (Global Interpreter Lock)**
```python
# GIL de Python: solo un thread ejecuta bytecode a la vez

# Con threading:
Thread 1: ──[GIL]──[espera]──[GIL]──[espera]──
Thread 2: ──[espera]──[GIL]──[espera]──[GIL]──
# → Competencia por el GIL incluso cuando esperan I/O

# Con asyncio:
Thread único: ──[trabaja]──[espera I/O]──[trabaja]──
# → No hay competencia, un solo thread, no hay GIL problem
```

**Justificación**:
Nuestro servidor es **I/O bound** (red, llamadas HTTP). La mayoría del tiempo se gasta esperando:
- Datos del socket del cliente → `await reader.readline()`
- Respuesta del LLM (HTTP) → `await client.post()`
- Escritura al socket → `await writer.drain()`

AsyncIO permite **miles de conexiones simultáneas** con bajo overhead de memoria y CPU, y sin los problemas del GIL de Python.

### ✅ Por qué Separar Servidor TCP y Gateway WebSocket

**Arquitectura de Gateway** (patrón de diseño Adapter/Bridge):

#### Razones Clave:

**1. Separación de responsabilidades (SRP - Single Responsibility Principle)**
```python
# Gateway (gateway/ws_gateway.py)
# - Solo maneja: WebSocket ↔ TCP
# - No sabe: Lógica de negocio, LLM, rate limiting
# - Responsabilidad: Traducción de protocolos

# Servidor (app/server.py + client_handler.py)
# - Solo maneja: Lógica de negocio, LLM, rate limiting
# - No sabe: WebSocket, HTTP, detalles de transporte
# - Responsabilidad: Procesamiento de mensajes
```

**2. Simplicidad de testing**
```bash
# Probar servidor TCP directamente (sin gateway)
telnet localhost 5001
> Hola
< Usuario-1 conectado. Bienvenido a PsicoIA...

# Probar con netcat
nc localhost 5001
> ¿Cómo estás?
< [Respuesta del LLM]

# Sin necesidad de:
# - Abrir navegador
# - Configurar WebSocket
# - Cliente JavaScript
```

**3. Flexibilidad de protocolos**
```python
# Arquitectura extensible sin tocar el core:

HTTP REST API ──┐
                │
WebSocket ──────┼──→ [Gateway Layer] ──→ [TCP Server]
                │
gRPC ───────────┤
                │
MQTT ───────────┘

# Cada gateway es independiente:
# - gateway/ws_gateway.py    (actual)
# - gateway/http_gateway.py  (futuro)
# - gateway/grpc_gateway.py  (futuro)

# Servidor TCP NO CAMBIA
```

**4. Aislamiento de sesión (1:1 mapping)**
```python
# gateway/ws_gateway.py
async def bridge_ws_to_tcp(websocket):
    # Cada conexión WebSocket abre SU PROPIA conexión TCP
    reader, writer = await asyncio.open_connection(TCP_HOST, TCP_PORT)
    
    # Mapeo 1:1 garantizado:
    # WebSocket Cliente A ←→ TCP Conexión A ←→ Usuario-1
    # WebSocket Cliente B ←→ TCP Conexión B ←→ Usuario-2
    
    # ✅ No hay contaminación de estado entre usuarios
    # ✅ No hay mezcla de mensajes
    # ✅ Cada usuario tiene su propio canal aislado
```

**5. Ventajas adicionales**:
- ✅ **Testeable**: Cada componente se prueba independientemente
- ✅ **Extensible**: Agregar protocolos sin modificar lógica de negocio
- ✅ **Mantenible**: Bug en gateway no afecta al servidor TCP
- ✅ **Escalable**: Gateway y servidor pueden estar en máquinas diferentes
- ✅ **Reusable**: El servidor TCP puede ser usado por otros clientes

**Alternativa (monolito) - NO recomendado**:
```python
# ❌ Todo en un solo servidor
async def handle_connection(connection):
    if isinstance(connection, WebSocketConnection):
        # Lógica WebSocket aquí
        await handle_websocket(connection)
    elif isinstance(connection, TCPConnection):
        # Lógica TCP aquí
        await handle_tcp(connection)
    
    # Problemas:
    # - Código complejo y acoplado
    # - Difícil de testear
    # - Cambios en un protocolo afectan a otros
    # - Violación del SRP
```

**Flujo de datos**:
```
Navegador → [WebSocket] → Gateway → [TCP] → Servidor → LLM
         ←             ←          ←       ←          ←
         
Cliente nativo → [TCP directo] → Servidor → LLM
              ←                ←          ←
```

### ✅ Por qué Almacenar Historial en RAM y No en Base de Datos

**Decisión para prototipo**:

| Opción | Ventajas | Desventajas |
|--------|----------|-------------|
| **RAM** | - Simple<br>- Rápido (< 1ms)<br>- Sin dependencias<br>- Sin configuración | - No persistente<br>- Pierde datos al reiniciar<br>- Limitado por memoria |
| **DB** | - Persistente<br>- Escalable<br>- Consultas complejas | - Complejidad (setup, migraciones)<br>- Latencia adicional (5-50ms)<br>- Dependencia externa |

#### Razones Clave:

**1. Prototipado rápido**
```python
# Implementación en RAM: ~20 líneas
_histories: dict[str, list[dict]] = defaultdict(list)

async def get_history(conversation_id: str) -> list[dict]:
    return list(_histories.get(conversation_id, []))

async def append_user(conversation_id: str, text: str):
    _histories[conversation_id].append({"role": "user", "content": text})

# Implementación con DB: ~200+ líneas
# - Configurar conexión async (asyncpg/motor)
# - Crear tablas (migrations)
# - Manejo de transacciones
# - Pool de conexiones
# - Manejo de errores de red
# - Reintentos, timeouts
```

**2. Suficiente para demostración**
```python
# Para pruebas y demos:
# ✅ 100-1000 usuarios concurrentes: OK
# ✅ Historial de 50-200 mensajes por usuario: OK
# ✅ Memoria: ~1MB por 1000 mensajes
# ✅ Latencia: < 1ms (acceso a dict)

# Para producción:
# ❌ Miles de usuarios persistentes
# ❌ Historial de años
# ❌ Análisis de datos históricos
# → Entonces sí necesitamos DB
```

**3. Ruta de migración clara (interfaz definida)**
```python
# Interfaz actual (abstracta del almacenamiento):
async def get_history(conversation_id: str) -> list[dict]
async def append_user(conversation_id: str, text: str) -> None
async def append_assistant(conversation_id: str, text: str) -> None

# Migración futura: cambiar implementación, no la interfaz
async def get_history(conversation_id: str) -> list[dict]:
    # Versión RAM (actual):
    return list(_histories.get(conversation_id, []))
    
    # Versión PostgreSQL (futuro):
    # async with db_pool.acquire() as conn:
    #     rows = await conn.fetch(
    #         "SELECT role, content FROM messages "
    #         "WHERE user_id = $1 ORDER BY timestamp",
    #         conversation_id
    #     )
    #     return [dict(row) for row in rows]

# ✅ Código cliente NO CAMBIA
# ✅ Solo cambiar llm_client.py
```

**4. Protección con Locks (evita race conditions)**
```python
# Sin locks (❌ race condition):
_histories[user] = [...]
# Thread A: lee lista
# Thread B: modifica lista
# Thread A: escribe lista (sobrescribe cambios de B)

# Con locks (✅ thread-safe):
_locks: dict[str, asyncio.Lock] = {}

async def append_user(conversation_id: str, text: str):
    async with _get_lock(conversation_id):
        _histories[conversation_id].append(
            {"role": "user", "content": text}
        )
    # ✅ Solo una coroutine modifica el historial a la vez
    # ✅ Garantía de atomicidad
```

**5. Sin dependencias externas**
```bash
# RAM: no requiere
docker-compose up  # ✅ Funciona inmediatamente

# Con DB: requiere
# - PostgreSQL/MongoDB container
# - Schema/migrations
# - Configuración de credenciales
# - Manejo de conexiones
# - ¿DB no disponible? → Sistema no funciona
```

**Justificación**:
1. **Objetivo educativo**: Prioridad es entender sockets, asyncio, concurrencia (no administración de DB)
2. **Prototipo funcional rápido**: De la idea a código funcional en horas, no días
3. **Suficiente para el alcance**: Demo universitaria con 10-20 usuarios simultáneos
4. **Migración preparada**: La interfaz permite cambiar el backend sin tocar la lógica de negocio

**Performance comparado**:
```python
# Acceso a RAM:
await get_history("Usuario-1")  # < 0.1ms

# Acceso a PostgreSQL local:
await db.fetch("SELECT ...")     # 5-10ms

# Acceso a PostgreSQL remoto:
await db.fetch("SELECT ...")     # 20-50ms

# Para nuestra app: la diferencia es insignificante
# Para 10,000 req/s: la diferencia es crítica → necesitamos Redis
```

### ✅ Por qué Docker Compose

**Beneficios de la containerización**:

#### Razones Clave:

**1. Reproducibilidad del entorno**
```bash
# Desarrollador A (Windows 11, Python 3.11)
docker-compose up
# → Usa Python 3.12 del contenedor

# Desarrollador B (Mac M1, Python 3.9)
docker-compose up
# → Usa Python 3.12 del contenedor

# Servidor producción (Ubuntu 22.04)
docker-compose up
# → Usa Python 3.12 del contenedor

# ✅ Mismo comportamiento en todas las máquinas
# ✅ "Funciona en mi máquina" → "Funciona en TODAS las máquinas"
```

**2. Orquestación automática de servicios**
```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["5001:5001"]
    
  gateway:
    image: psicoia:latest  # Reutiliza imagen de 'app'
    ports: ["8765:8765"]
    environment:
      - TCP_HOST=app  # Nombre del servicio = hostname DNS
    depends_on:
      app:
        condition: service_started  # Espera a que app esté listo

# ✅ Docker Compose maneja:
# - Orden de inicio (app antes que gateway)
# - Red interna automática
# - DNS entre servicios (gateway puede hacer `connect('app', 5001)`)
# - Variables de entorno
# - Reinicio automático si se cae
```

**3. Aislamiento completo**
```python
# Sin Docker:
# - pip install en sistema global
# - Conflictos de versiones (httpx 0.24 vs 0.27)
# - Variables de entorno del usuario
# - Puerto 5001 puede estar ocupado

# Con Docker:
# ✅ Cada contenedor tiene su propio:
#    - Sistema de archivos
#    - Espacio de procesos
#    - Network namespace (puertos)
#    - Variables de entorno
# ✅ No contamina el sistema host
# ✅ No hay conflictos
```

**4. Despliegue sencillo (un solo comando)**
```bash
# Sin Docker (setup manual):
# 1. Instalar Python 3.12
sudo apt install python3.12
# 2. Crear virtualenv
python3.12 -m venv venv
source venv/bin/activate
# 3. Instalar dependencias
pip install -r requirements.txt
# 4. Configurar .env
cp .env.example .env
vim .env  # Editar manualmente
# 5. Abrir 2 terminales
# Terminal 1:
python -m app.server
# Terminal 2:
python -m gateway.ws_gateway
# → 5 pasos, propenso a errores

# Con Docker (setup automático):
docker-compose up -d
# → 1 comando, todo funciona
# ✅ Dependencias instaladas automáticamente
# ✅ Ambos servicios corriendo
# ✅ Configuración desde .env
# ✅ Redes configuradas
```

**5. Gestión de dependencias y servicios**
```yaml
# Fácil agregar más servicios:
services:
  app:
    build: .
  
  gateway:
    image: psicoia:latest
  
  # Futuro: agregar PostgreSQL
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: psicoia
      POSTGRES_PASSWORD: secret
  
  # Futuro: agregar Redis
  redis:
    image: redis:7-alpine
  
  # Futuro: agregar monitoring
  prometheus:
    image: prom/prometheus

# docker-compose up → Todos se levantan con sus dependencias
```

**Comparación**:

| Aspecto | Sin Docker | Con Docker |
|---------|------------|------------|
| **Setup** | 5+ pasos manuales | 1 comando |
| **Reproducibilidad** | Depende del SO y versiones | 100% reproducible |
| **Aislamiento** | Sistema global | Contenedores aislados |
| **Portabilidad** | "Funciona en mi máquina" | Funciona en todas |
| **Dependencias** | Conflictos posibles | Totalmente aisladas |
| **Documentación** | README largo | docker-compose.yml es la doc |
| **CI/CD** | Setup complejo | `docker build && docker push` |

**Comandos útiles**:
```bash
# Levantar servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f app

# Reiniciar un servicio
docker-compose restart gateway

# Bajar todo
docker-compose down

# Reconstruir imágenes
docker-compose build --no-cache

# Ver estado
docker-compose ps

# Entrar a un contenedor
docker-compose exec app bash
```

**Justificación**:
Para un proyecto que debe ser **defendido y demostrado** ante un profesor, Docker Compose garantiza que:
- ✅ Funciona en la máquina del profesor sin setup
- ✅ No hay "pero en mi máquina funcionaba"
- ✅ La demo es profesional y confiable
- ✅ Demuestra conocimiento de DevOps moderno

---

## Observabilidad y Monitoreo

### Sistema de Logs

**Niveles de logging**:
```python
# app/utils/logger.py
log.debug("Detalle técnico")      # Desarrollo
log.info("Evento importante")     # Producción
log.warning("Situación atípica")  # Alertas
log.error("Error recuperable")    # Errores
log.exception("Error crítico")    # Con stack trace
```

**Logs estructurados**:
```python
log.info(f"[{trace_id}] POST {url} model={model} len={len(user_text)}")
# [Usuario-3:m5] POST https://api.groq.com/... model=llama-3.1 len=42

log.info(f"[{trace_id}] ← LLM ok ({len(llm_reply)} chars) {dt_ms:.0f} ms")
# [Usuario-3:m5] ← LLM ok (156 chars) 847 ms
```

### Trazabilidad (Trace ID)

**¿Qué es un trace_id?**
Un identificador único que vincula todas las operaciones de una request.

**Formato**: `Usuario-N:mM`
- `Usuario-N`: Cliente específico
- `mM`: Número de mensaje de ese cliente

**Ejemplo de flujo completo**:
```
[Usuario-3] Conexión desde ('192.168.1.100', 54321)
[Usuario-3:m1] → LLM start (len=42)
[Usuario-3:m1] POST https://api.groq.com/openai/v1/chat/completions
[Usuario-3:m1] ← LLM ok (156 chars) 847 ms
[Usuario-3:m2] → LLM start (len=58)
[Usuario-3:m2] ← LLM ok (203 chars) 1205 ms
[Usuario-3] Conexión cerrada
```

**Ventajas**:
- Correlacionar logs distribuidos
- Medir latencia por operación
- Debugging facilitado
- Análisis de performance

### Rate Limiting

**Implementación**: Ventana deslizante (Sliding Window)

```python
class SlidingWindowLimiter:
    def __init__(self, max_events: int, window_seconds: int):
        self.max = max_events
        self.win = window_seconds
        self.events = deque()  # Timestamps de eventos
    
    def allow(self) -> bool:
        now = time.monotonic()
        
        # Eliminar eventos fuera de la ventana
        while self.events and now - self.events[0] > self.win:
            self.events.popleft()
        
        # Verificar si hay espacio
        if len(self.events) < self.max:
            self.events.append(now)
            return True
        return False
```

**Ejemplo de uso**:
```
Configuración: 10 mensajes por 60 segundos

Mensajes del usuario:
t=0s:  msg1 ✅ (1/10)
t=1s:  msg2 ✅ (2/10)
...
t=9s:  msg10 ✅ (10/10)
t=10s: msg11 ❌ Bloqueado
t=61s: msg12 ✅ (msg1 salió de la ventana)
```

### Métricas Clave

**Disponibles en los logs**:
1. **Latencia del LLM**: Tiempo de respuesta del modelo
2. **Conexiones activas**: Número de usuarios simultáneos
3. **Rate limiting**: Cuántos requests se bloquean
4. **Errores**: Tasa de fallos del LLM

**Ejemplo de log agregado**:
```
[INFO] TCP server escuchando en ('0.0.0.0', 5001)
[INFO] [Usuario-1] Conexión desde ('127.0.0.1', 52847)
[INFO] [Usuario-1:m1] → LLM start (len=45)
[INFO] [Usuario-1:m1] ← LLM ok (198 chars) 923 ms
[WARNING] [Usuario-2:m15] Rate limit excedido
[ERROR] [Usuario-3:m8] Groq error: 429 Rate Limit
```

---

## Docker y Containerización

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias
COPY requirements.txt ./

# Instalar dependencias Python
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Exponer puertos
EXPOSE 5001 8765
```

**Capas de la imagen**:
1. **Base**: Python 3.12 slim (~45MB)
2. **Build tools**: Compiladores para librerías nativas
3. **Dependencias Python**: asyncio, httpx, websockets, etc.
4. **Código aplicación**: Nuestros archivos .py

### Docker Compose

```yaml
services:
  app:
    build: .
    image: psicoia:latest
    container_name: psicoia_app
    env_file: .env
    command: ["python", "-m", "app.server"]
    ports:
      - "${APP_PORT:-5001}:5001"

  gateway:
    image: psicoia:latest  # Reutiliza la misma imagen
    container_name: psicoia_gateway
    env_file: .env
    environment:
      - TCP_HOST=app  # Nombre del servicio como hostname
      - TCP_PORT=5001
      - WS_HOST=0.0.0.0
      - WS_PORT=8765
    command: ["python", "-m", "gateway.ws_gateway"]
    ports:
      - "8765:8765"
    depends_on:
      app:
        condition: service_started
```

**¿Cómo se comunican los contenedores?**

Docker Compose crea una **red privada** donde:
- Cada contenedor tiene su hostname = nombre del servicio
- `gateway` puede acceder a `app` usando `TCP_HOST=app`
- La resolución DNS es automática

```
┌─────────────────────────────────┐
│  Red Docker "psicoia_default"   │
│                                 │
│  ┌──────────┐    ┌───────────┐ │
│  │   app    │    │  gateway  │ │
│  │  :5001   │←───│  :8765    │ │
│  └──────────┘    └───────────┘ │
│        ↑              ↑         │
└────────┼──────────────┼─────────┘
         │              │
      Puerto        Puerto
      5001          8765
```

### Comandos Docker Útiles

```bash
# Construir y levantar servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f app

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Reconstruir imagen
docker-compose build --no-cache

# Ver contenedores corriendo
docker-compose ps

# Entrar a un contenedor
docker-compose exec app bash
```

### Simulación de Condiciones de Red

**Para demostrar robustez** puedes simular:

1. **Latencia de red**:
   ```bash
   # En Linux (dentro del contenedor)
   tc qdisc add dev eth0 root netem delay 100ms
   ```

2. **Pérdida de paquetes**:
   ```bash
   tc qdisc add dev eth0 root netem loss 5%
   ```

3. **Límite de ancho de banda**:
   ```bash
   tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms
   ```

4. **Desconexión abrupta**:
   ```bash
   docker-compose stop app
   # El gateway manejará el error y notificará al cliente
   ```

**Nuestro sistema es resiliente porque**:
- **Timeouts configurables**: `LLM_TIMEOUT_SECONDS`
- **Reintentos automáticos**: `LLM_MAX_RETRIES`
- **Backoff exponencial**: Espera cada vez más entre reintentos
- **Manejo de errores**: Notifica al usuario si algo falla

---

## Posibles Preguntas del Profesor

### 1. ¿Cómo funciona el servidor?

**Respuesta**:

El servidor es un **servidor TCP asíncrono** basado en `asyncio`. Funciona así:

1. Se crea un **socket de escucha** en el puerto 5001
2. El socket acepta conexiones entrantes de forma **no bloqueante**
3. Por cada cliente que se conecta, se crea automáticamente una **coroutine independiente** (`handle_client`)
4. Cada coroutine maneja el ciclo de vida completo de su cliente: recibir mensajes, procesar con el LLM, enviar respuestas
5. El **event loop** de asyncio coordina todas las coroutines, alternando entre ellas cuando esperan I/O

**Código clave**:
```python
server = await asyncio.start_server(handle_client, host="0.0.0.0", port=5001)
async with server:
    await server.serve_forever()  # Loop infinito
```

---

### 2. ¿Cómo gestionan múltiples clientes?

**Respuesta**:

Usamos **concurrencia cooperativa** con `asyncio`:

1. **Una coroutine por cliente**: Cada conexión TCP tiene su propia coroutine `handle_client()`
2. **Aislamiento de estado**: Cada cliente tiene su propio:
   - Reader/Writer (socket)
   - Rate limiter
   - Historial conversacional
   - Identificador único (`Usuario-N`)

3. **No hay bloqueos**: Cuando un cliente espera datos (`await reader.readline()`), el event loop atiende a otros

**Capacidad**: Podemos manejar **miles de clientes** simultáneamente con un solo hilo, porque:
- No usamos hilos pesados
- Las coroutines son livianas (~1KB cada una)
- La mayor parte del tiempo se espera I/O (no se usa CPU)

---

### 3. ¿Cómo manejan la concurrencia?

**Respuesta**:

Implementamos **múltiples niveles de control de concurrencia**:

#### Nivel 1: Conexiones simultáneas (ilimitadas)
```python
# Asyncio maneja automáticamente miles de conexiones
server = await asyncio.start_server(...)
```

#### Nivel 2: Rate limiting por usuario
```python
# Cada cliente tiene un rate limiter que previene flooding
limiter = SlidingWindowLimiter(max_messages=10, window_seconds=60)
if not limiter.allow():
    return "Demasiados mensajes"
```

#### Nivel 3: Semáforo global para el LLM
```python
# Limita cuántas llamadas simultáneas al LLM pueden haber
SEM_GLOBAL = asyncio.Semaphore(MAX_IN_FLIGHT)
async with SEM_GLOBAL:
    llm_reply = await llm_generate(...)
```

**¿Por qué tres niveles?**
- **Nivel 1**: Aceptamos todas las conexiones para no rechazar clientes
- **Nivel 2**: Prevenimos que un usuario malicioso sature el sistema
- **Nivel 3**: Protegemos el recurso compartido (API del LLM) contra sobrecarga

---

### 4. ¿Qué pasa si dos usuarios mandan mensajes al mismo tiempo?

**Respuesta**:

**No hay problema** porque cada usuario está completamente aislado:

1. **Sockets independientes**: Cada cliente tiene su propio par reader/writer
2. **Coroutines independientes**: No comparten variables (excepto estructuras thread-safe)
3. **Historial separado**: Usamos `conversation_id` único como clave en el diccionario

**Ejemplo**:
```python
# Cliente 1 envía "Hola"
Usuario-1:m1 → llm_generate("Hola", conversation_id="Usuario-1")
# Mientras espera respuesta del LLM...

# Cliente 2 envía "Ayuda"
Usuario-2:m1 → llm_generate("Ayuda", conversation_id="Usuario-2")
# Ambos progresan independientemente

# Historiales separados:
_histories["Usuario-1"] = [{"role": "user", "content": "Hola"}, ...]
_histories["Usuario-2"] = [{"role": "user", "content": "Ayuda"}, ...]
```

**Sincronización**: El único punto de sincronización es el **semáforo global**, que garantiza que no haya más de N llamadas simultáneas al LLM, pero no mezcla los datos de los usuarios.

---

### 5. ¿Qué pasaría sin asyncio?

**Respuesta**:

Sin `asyncio`, tendríamos que usar **threads o multiprocessing**, lo cual tiene serios inconvenientes:

#### Opción A: Un hilo por cliente
```python
import threading

def handle_client(socket):
    # Código bloqueante
    data = socket.recv(1024)  # Bloquea este hilo
    # ...

for connection in connections:
    thread = threading.Thread(target=handle_client, args=(connection,))
    thread.start()
```

**Problemas**:
- ❌ **Escalabilidad limitada**: ~100-1000 hilos máximo
- ❌ **Consumo de memoria**: 8MB × 1000 hilos = 8GB RAM solo en stacks
- ❌ **Context switching costoso**: Cambios de hilo involucran al kernel
- ❌ **Sincronización compleja**: Necesitamos locks para el historial compartido
- ❌ **Race conditions**: Fácil introducir bugs de concurrencia

#### Opción B: Blocking I/O secuencial
```python
# Un solo hilo atiende clientes uno a uno
while True:
    data = socket.recv(1024)  # Bloquea todo el servidor
    process(data)
```

**Problemas**:
- ❌ **Un solo cliente a la vez**: El segundo cliente espera que termine el primero
- ❌ **Latencia inaceptable**: Si el LLM tarda 3 segundos, todos esperan

#### Con asyncio (nuestra solución):
- ✅ **Miles de clientes** con bajo overhead
- ✅ **Concurrencia cooperativa** sin race conditions
- ✅ **Código claro** con sintaxis `async/await`
- ✅ **Eficiencia**: CPU solo cuando hay trabajo real

---

### 6. ¿Qué hace exactamente el socket?

**Respuesta**:

Un **socket** es la interfaz de programación para comunicación de red. En nuestro caso:

#### Socket del Servidor (escucha)
```python
# Crea un socket que "escucha" conexiones entrantes
server = await asyncio.start_server(...)
```

**Internamente hace**:
1. `socket.socket(AF_INET, SOCK_STREAM)` - Crea socket TCP
2. `socket.bind(("0.0.0.0", 5001))` - Asocia a IP y puerto
3. `socket.listen(...)` - Pone en modo escucha
4. `socket.accept()` - Acepta conexiones (retorna un nuevo socket por cliente)

#### Socket del Cliente (por conexión)
```python
async def handle_client(reader, writer):
    # reader: StreamReader (wrapper de socket.recv)
    # writer: StreamWriter (wrapper de socket.send)
```

**Operaciones básicas**:
- `reader.readline()` → Lee datos del socket hasta `\n`
- `writer.write(data)` → Escribe datos al buffer
- `writer.drain()` → Fuerza envío del buffer al socket

**A bajo nivel** (en C, simplificado):
```c
// Servidor
int server_fd = socket(AF_INET, SOCK_STREAM, 0);
bind(server_fd, addr, ...);
listen(server_fd, backlog);

while (1) {
    int client_fd = accept(server_fd, ...);  // Nuevo socket por cliente
    handle_client(client_fd);
}

// Cliente
int client_fd = socket(AF_INET, SOCK_STREAM, 0);
connect(client_fd, server_addr, ...);
send(client_fd, "Hola", 4, 0);
recv(client_fd, buffer, 1024, 0);
```

**En Python con asyncio**:
Asyncio envuelve estos sockets en objetos de alto nivel (`StreamReader/Writer`) que son **no bloqueantes** y se integran con el event loop.

---

### 7. ¿Cómo garantizan que el mensaje llegue ordenado?

**Respuesta**:

**TCP garantiza el orden automáticamente**. No necesitamos hacer nada especial. Aquí está cómo:

#### Mecanismo de TCP

1. **Números de secuencia**:
   - Cada byte tiene un número único
   - Ejemplo: "Hola mundo" se numera: H=100, o=101, l=102, ...

2. **Reordenamiento en el receptor**:
   - Si los paquetes llegan desordenados, TCP los reordena antes de entregarlos a la aplicación

3. **ACKs (Acknowledgments)**:
   - El receptor confirma la recepción con el número del próximo byte esperado

**Ejemplo visual**:
```
Emisor envía:
Paquete 1: [Seq=100] "Hola "
Paquete 2: [Seq=105] "mundo"

Red desordena:
Paquete 2 llega primero ← [Seq=105] "mundo"
Paquete 1 llega después ← [Seq=100] "Hola "

TCP en receptor:
Buffer: [100: "Hola ", 105: "mundo"]
Reordena por Seq: 100, 105
Entrega a app: "Hola mundo"  ← ¡En orden!
```

#### En nuestro código

```python
# Enviamos mensaje con \n como delimitador
writer.write("Hola\nmundo\n".encode("utf-8"))
await writer.drain()

# Receptor lee línea por línea
line1 = await reader.readline()  # "Hola\n"
line2 = await reader.readline()  # "mundo\n"
# Siempre llegan en orden por garantía de TCP
```

**Nota**: Si usáramos UDP en vez de TCP, **no** habría garantía de orden y tendríamos que implementarlo nosotros con números de secuencia adicionales.

---

### 8. ¿Qué ventaja aporta el gateway WebSocket?

**Respuesta**:

El gateway **desacopla el protocolo de transporte de la lógica de negocio**. Ventajas clave:

#### 1. Compatibilidad con navegadores
- **Problema**: Los navegadores no pueden crear sockets TCP directos (seguridad)
- **Solución**: WebSocket es un protocolo estándar web
- El gateway traduce: WebSocket ↔ TCP

#### 2. Separación de responsabilidades
```
Gateway:              Servidor:
- Maneja WebSocket    - Maneja lógica de negocio
- Traduce protocolos  - Gestiona historial
- Buffer de mensajes  - Integra con LLM
```

#### 3. Extensibilidad
Agregar más protocolos sin tocar el servidor:
```
HTTP REST API ─┐
               ├─→ [Gateway] ─→ [Servidor TCP]
WebSocket ─────┤
               │
gRPC ──────────┘
```

#### 4. Escalabilidad
- **Gateway horizontal**: Múltiples instancias del gateway, un servidor
- **Balanceo de carga**: Distribuir clientes entre gateways

```
Cliente 1 → Gateway A ┐
Cliente 2 → Gateway A ├─→ Servidor TCP
Cliente 3 → Gateway B │
Cliente 4 → Gateway B ┘
```

#### 5. Testing simplificado
```bash
# Probar servidor sin gateway
telnet localhost 5001
> Hola
< Usuario-1 conectado...

# Probar gateway independientemente
# Mock del servidor TCP para tests
```

**Patrón de diseño**: **Adapter/Bridge** - Adapta una interfaz (WebSocket) a otra (TCP).

---

### 9. ¿Qué problema resuelve Docker?

**Respuesta**:

Docker resuelve el problema clásico de **"funciona en mi máquina"** mediante:

#### 1. Reproducibilidad
```bash
# Desarrollador A (Windows)
docker-compose up

# Desarrollador B (Mac)
docker-compose up

# Servidor producción (Linux)
docker-compose up

# → Mismo comportamiento en todas las máquinas
```

#### 2. Encapsulación de dependencias
```dockerfile
# Todo lo necesario está en la imagen
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

**Sin Docker**:
- "¿Tienes Python 3.12?"
- "¿Instalaste httpx?"
- "¿Tu versión de asyncio es compatible?"
- "¿Configuraste las variables de entorno?"

**Con Docker**: Solo necesitas Docker instalado.

#### 3. Aislamiento
- Contenedores no interfieren con el sistema host
- Cada contenedor tiene su propio:
  - Sistema de archivos
  - Espacio de procesos
  - Red virtual

#### 4. Portabilidad
```bash
# Desarrollo local
docker-compose up -d

# Subir a la nube
docker push psicoia:latest

# Deploy en AWS/GCP/Azure
docker pull psicoia:latest
docker run ...
```

#### 5. Orquestación simplificada
```yaml
# docker-compose.yml define toda la infraestructura
services:
  app:       # Servidor TCP
  gateway:   # Gateway WebSocket
  db:        # Base de datos (futuro)
  nginx:     # Reverse proxy (futuro)
```

**Sin Docker**:
- Instalar y configurar cada servicio manualmente
- Gestionar inicio/parada de múltiples procesos
- Configurar red entre servicios

**Con Docker**:
```bash
docker-compose up -d  # Todo listo
```

#### 6. Debugging y desarrollo
```bash
# Ver logs en tiempo real
docker-compose logs -f app

# Entrar al contenedor
docker-compose exec app bash

# Reiniciar sin perder estado
docker-compose restart gateway
```

---

### 10. ¿Cómo está organizado el código?

**Respuesta**:

El código sigue una **arquitectura en capas** con **separación de concerns**:

```
┌─────────────────────────────────────┐
│         Presentación                │  web/client_web.html
│  (Interface de usuario)             │
└──────────────┬──────────────────────┘
               │ WebSocket
┌──────────────▼──────────────────────┐
│         Gateway Layer               │  gateway/ws_gateway.py
│  (Traducción de protocolos)         │
└──────────────┬──────────────────────┘
               │ TCP
┌──────────────▼──────────────────────┐
│      Application Layer              │  app/server.py
│  (Lógica de negocio)                │  app/client_handler.py
└──────────────┬──────────────────────┘
               │
     ┌─────────┼─────────┐
     │         │         │
┌────▼───┐ ┌──▼───┐ ┌──▼────┐
│Services│ │Utils │ │Prompts│
│        │ │      │ │       │
│llm_    │ │rate_ │ │prompt │
│client  │ │limiter│ │general│
└────────┘ └──────┘ └───────┘
```

#### Módulos principales

**1. `app/server.py`** - Punto de entrada
- Inicializa el servidor TCP
- Configura asyncio
- Delega a `client_handler`

**2. `app/client_handler.py`** - Core del negocio
- Maneja ciclo de vida del cliente
- Implementa rate limiting
- Orquesta llamadas al LLM

**3. `app/services/llm_client.py`** - Integración externa
- Cliente HTTP para Groq
- Gestión de historial
- Reintentos y timeouts

**4. `app/utils/`** - Utilidades compartidas
- `logger.py`: Logging estructurado
- `rate_limiter.py`: Control de tasa

**5. `gateway/ws_gateway.py`** - Protocolo bridge
- Servidor WebSocket
- Proxy bidireccional a TCP

**6. `app/config.py`** - Configuración centralizada
- Variables de entorno
- Settings con Pydantic

#### Principios de diseño aplicados

1. **Single Responsibility**: Cada módulo tiene un propósito claro
2. **Dependency Injection**: Config se inyecta, no se importa globalmente en lógica
3. **Separation of Concerns**: Gateway no sabe de LLM, LLM no sabe de sockets
4. **Open/Closed**: Fácil agregar nuevos protocolos sin modificar el core

---

### 11. ¿Qué mecanismos de seguridad tiene el sistema?

**Respuesta**:

Aunque es un prototipo educativo, implementamos varias **medidas de protección**:

#### 1. Rate Limiting (prevención de flooding)
```python
# Límite: 10 mensajes por 60 segundos por usuario
limiter = SlidingWindowLimiter(max_messages=10, window_seconds=60)
```

**Protege contra**:
- Usuarios maliciosos que envían miles de mensajes
- Ataques de denegación de servicio (DoS)
- Sobrecarga accidental

#### 2. Semáforo global (protección del recurso compartido)
```python
SEM_GLOBAL = asyncio.Semaphore(MAX_IN_FLIGHT)
```

**Protege contra**:
- Sobrecarga de la API del LLM
- Costos excesivos (API cobra por request)
- Throttling del proveedor

#### 3. Timeouts (prevención de conexiones zombies)
```python
async with httpx.AsyncClient(timeout=30) as client:
    resp = await client.post(...)
```

**Protege contra**:
- Llamadas que se cuelgan indefinidamente
- Agotamiento de recursos (sockets, memoria)

#### 4. Validación de entrada
```python
msg = data.decode().strip()
if not msg:
    continue  # Ignora mensajes vacíos
```

#### 5. Manejo de excepciones
```python
try:
    # Código que puede fallar
except Exception as e:
    log.exception(f"Error: {e}")
    # Sistema sigue funcionando
```

**Mejoras de seguridad futuras**:
- [ ] Autenticación (JWT tokens)
- [ ] Cifrado TLS/SSL
- [ ] Sanitización de input (prevenir injection)
- [ ] Límite de longitud de mensaje
- [ ] Blacklist de IPs abusivas

---

### 12. ¿Cómo escalaría el sistema para producción?

**Respuesta**:

Para llevar esto a producción, implementaría:

#### 1. Base de datos persistente
```python
# Reemplazar dict en RAM por PostgreSQL
async def get_history(conversation_id):
    return await db.fetch(
        "SELECT * FROM messages WHERE user_id = $1 ORDER BY timestamp",
        conversation_id
    )
```

#### 2. Balanceo de carga
```
              ┌─→ Servidor 1
Load Balancer ├─→ Servidor 2
              └─→ Servidor 3
```

#### 3. Cache distribuido
```python
# Redis para historial de sesión
import aioredis
redis = await aioredis.create_redis_pool("redis://localhost")
history = await redis.get(f"session:{user_id}")
```

#### 4. Message Queue para desacoplamiento
```
Cliente → Gateway → RabbitMQ → Workers → LLM
```

**Ventajas**:
- Procesamiento asíncrono
- Reintentos automáticos
- Escalado independiente de workers

#### 5. Observabilidad profesional
```python
# Prometheus para métricas
from prometheus_client import Counter, Histogram

requests_total = Counter("requests_total", "Total requests")
latency = Histogram("llm_latency_seconds", "LLM latency")
```

#### 6. Seguridad robusta
- **TLS/SSL**: Cifrado en tránsito
- **Autenticación**: JWT o OAuth2
- **Rate limiting distribuido**: Redis + sliding window
- **WAF**: Web Application Firewall

#### 7. Kubernetes para orquestación
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: psicoia-server
spec:
  replicas: 5  # 5 instancias del servidor
  template:
    spec:
      containers:
      - name: app
        image: psicoia:latest
```

**Auto-scaling**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

### 13. ¿Qué pasa si el LLM falla o tarda mucho?

**Respuesta**:

Tenemos **múltiples capas de resiliencia**:

#### 1. Timeout configurable
```python
async with httpx.AsyncClient(timeout=30) as client:
    resp = await client.post(...)
```

Si el LLM no responde en 30 segundos → TimeoutError

#### 2. Reintentos con backoff exponencial
```python
for attempt in range(1, MAX_RETRIES + 1):
    try:
        resp = await client.post(...)
        if resp.status_code == 429:  # Too Many Requests
            wait = BACKOFF_INITIAL * (2 ** (attempt - 1))
            await asyncio.sleep(wait)
            continue
        break
    except httpx.RequestError:
        # Reintenta
        continue
```

**Tiempos de espera**:
- Intento 1: 0s
- Intento 2: 2s (backoff)
- Intento 3: 4s (backoff × 2)
- Intento 4: 8s (backoff × 4)

#### 3. Respuesta de fallback
```python
except Exception as e:
    log.error(f"Groq error: {e}")
    return "Ocurrió un error. Por favor, intentá de nuevo."
```

El usuario recibe un mensaje claro en vez de timeout silencioso.

#### 4. Semáforo protege al sistema
```python
async with SEM_GLOBAL:  # Solo N pueden llamar al LLM simultáneamente
    llm_reply = await llm_generate(...)
```

Si el LLM está lento, otros usuarios esperan en la cola en vez de abrumar la API.

#### 5. Logs detallados para debugging
```python
log.warning(f"[{trace_id}] LLM retry {attempt}/{MAX_RETRIES} in {wait:.2f}s")
log.error(f"[{trace_id}] Groq error: {e}")
```

**Mejora futura**: Circuit breaker pattern
```python
# Si 5 requests fallan seguidos, deja de intentar por 60s
# Evita saturar el LLM si está caído
```

---

### 14. ¿Por qué usan `readline()` en vez de `read()`?

**Respuesta**:

`readline()` es más apropiado para protocolos basados en texto:

#### Ventajas de readline()
```python
data = await reader.readline()  # Lee hasta \n
```

1. **Delimitación natural**: Cada línea es un mensaje completo
2. **Buffer automático**: Si llega medio mensaje, espera el resto
3. **Simplicidad**: No necesitamos implementar nuestro propio protocolo de framing

#### Con read() necesitaríamos:
```python
# ❌ Más complejo
data = await reader.read(1024)  # ¿Cuántos bytes leer?
# - ¿Qué pasa si el mensaje es más largo?
# - ¿Qué pasa si llegan 2 mensajes juntos?
# - Necesitamos buffer y lógica de parsing
```

#### Protocolo de mensajes
```
Cliente envía: "Hola\n"
              "¿Cómo estás?\n"

readline() retorna:
Primera llamada: "Hola\n"
Segunda llamada: "¿Cómo estás?\n"

# Cada mensaje está perfectamente delimitado
```

**Desventaja**: No apto para datos binarios o mensajes que contengan `\n` en el medio. Para eso usaríamos un protocolo con longitud prefijada.

---

### 15. ¿Qué es `writer.drain()` y por qué es necesario?

**Respuesta**:

`drain()` es crítico para el **control de flujo** y garantiza que los datos se envíen.

#### Sin drain()
```python
writer.write("Hola".encode())  # Solo escribe al buffer
# Los datos NO se envían inmediatamente al socket
```

#### Con drain()
```python
writer.write("Hola".encode())  # Escribe al buffer
await writer.drain()            # Espera a que se envíe todo
```

**¿Qué hace drain() internamente?**
1. Fuerza el flush del buffer al socket
2. Si el buffer está lleno, **espera** (yield) hasta que haya espacio
3. Implementa **backpressure**: si el cliente lee lento, el servidor espera

#### Escenario sin drain()
```python
# Servidor rápido, cliente lento
for i in range(10000):
    writer.write(f"Mensaje {i}\n".encode())
    # Sin drain(), el buffer crece indefinidamente
    # → Out of Memory
```

#### Con drain() (correcto)
```python
for i in range(10000):
    writer.write(f"Mensaje {i}\n".encode())
    await writer.drain()  # Espera si el buffer está lleno
    # → Control de flujo automático
```

**Analogía**: Es como un grifo con sensor. Si el recipiente está lleno, el grifo espera antes de seguir vertiendo agua.

---

### 16. ¿Qué pasa si un cliente se desconecta abruptamente?

**Respuesta**:

Tenemos manejo robusto de desconexiones:

#### Detección de desconexión
```python
while True:
    data = await reader.readline()
    if not data:  # Socket cerrado
        break
```

Cuando el cliente cierra la conexión:
1. `reader.readline()` retorna `b''` (bytes vacío)
2. El loop detecta esto y sale con `break`
3. El bloque `finally` limpia recursos

#### Cleanup automático
```python
try:
    # Manejo del cliente
    pass
except Exception as e:
    log.exception(f"[{user}] Error: {e}")
finally:
    writer.close()              # Cierra el socket
    await writer.wait_closed()  # Espera confirmación
    log.info(f"[{user}] Conexión cerrada")
```

#### Escenarios cubiertos

1. **Cierre limpio** (cliente envía FIN):
   - TCP notifica EOF
   - `readline()` retorna vacío
   - Limpieza ordenada

2. **Cierre abrupto** (cable desconectado, proceso matado):
   - TCP espera timeout
   - Luego notifica error
   - Exception capturada en `except`

3. **Network partition**:
   - Keep-alive de TCP detecta conexión muerta
   - Socket genera error después de varios reintentos
   - Limpieza en `finally`

#### Historial del usuario
```python
# Al desconectar, el historial en RAM se MANTIENE
# Si se reconecta, obtiene nuevo ID pero puede recuperar sesión
# (aunque en la implementación actual, cada conexión = nueva sesión)
```

**Mejora futura**: Sesiones persistentes con tokens para reconectar y mantener contexto.

---

### 17. ¿Cómo funciona el semáforo exactamente?

**Respuesta**:

El semáforo es un **contador atómico** que limita el acceso concurrente a un recurso.

#### Concepto
```python
SEM_GLOBAL = asyncio.Semaphore(2)  # Contador inicial: 2
```

**Estado interno**:
- `_value`: Contador actual (2, 1, 0, ...)
- `_waiters`: Cola de coroutines esperando

#### Flujo de ejecución

```python
# Estado inicial: value=2

# Cliente A llega
async with SEM_GLOBAL:  # value=2-1=1, ENTRA
    await llm_generate()  # Llama al LLM

# Cliente B llega (mientras A espera)
async with SEM_GLOBAL:  # value=1-1=0, ENTRA
    await llm_generate()  # Llama al LLM

# Cliente C llega (mientras A y B esperan)
async with SEM_GLOBAL:  # value=0, BLOQUEA
    # C se agrega a _waiters y cede control
    await llm_generate()

# A termina
# → Sale del contexto
# → value=0+1=1
# → Despierta a C de _waiters
# → C entra y value=1-1=0

# B termina
# → value=0+1=1
# → Si hay más en _waiters, despierta al siguiente
```

#### Visualización
```
Tiempo →
─────────────────────────────────────────────
Cliente A: ────[LLM]────────
Cliente B:   ────[LLM]─────────
Cliente C:     ⏸️[ESPERA]⏸️───[LLM]────
Cliente D:         ⏸️[ESPERA]⏸️────[LLM]───
─────────────────────────────────────────────
Semáforo:  2→1→0    →1→0   →1→0
```

#### Sin semáforo
```python
# ❌ Todos llamarían al LLM simultáneamente
# → Sobrecarga del servidor
# → Rate limiting de Groq
# → Costos excesivos
# → Timeouts
```

#### Con semáforo
```python
# ✅ Máximo N llamadas simultáneas
# → Uso controlado de recursos
# → Cola de espera justa (FIFO)
# → Protección contra sobrecarga
```

---

### 18. ¿Dónde exactamente se usa paralelismo vs concurrencia?

**Respuesta**:

En nuestro proyecto usamos **concurrencia**, NO paralelismo real:

#### Definiciones

**Concurrencia** (lo que usamos):
- **Un solo hilo/núcleo** ejecuta múltiples tareas
- Las tareas se intercalan (time-slicing cooperativo)
- Cuando una espera I/O, otra ejecuta

**Paralelismo** (NO usado):
- **Múltiples hilos/núcleos** ejecutan tareas simultáneamente
- Ejecución realmente paralela en CPUs diferentes

#### En nuestro código

```python
# CONCURRENCIA (asyncio)
# Un solo thread del event loop
async def handle_client(reader, writer):
    while True:
        data = await reader.readline()  # Cede control aquí
        response = await llm_generate(data)  # Y aquí
        await writer.drain()  # Y aquí

# Múltiples clientes → múltiples coroutines
# Pero todas en UN SOLO THREAD
```

**Si usáramos paralelismo**:
```python
# PARALELISMO (multiprocessing)
from multiprocessing import Process

def handle_client(socket):
    # Cada cliente en su propio proceso
    # Realmente paralelo en múltiples CPUs
    pass

for connection in connections:
    p = Process(target=handle_client, args=(connection,))
    p.start()
```

#### ¿Por qué NO necesitamos paralelismo?

Nuestro trabajo es **I/O-bound**:
```
Tiempo de procesamiento:
┌─────────────────────────────┐
│ Esperando red: 95%          │████████████████████
│ Procesando CPU: 5%          │█
└─────────────────────────────┘

# CPU casi siempre está idle esperando I/O
# No tiene sentido usar múltiples CPUs
```

Si fuera **CPU-bound** (ej: procesamiento de video, cálculos complejos):
```
Tiempo de procesamiento:
┌─────────────────────────────┐
│ Esperando I/O: 5%           │█
│ Procesando CPU: 95%         │████████████████████
└─────────────────────────────┘

# Aquí SÍ necesitaríamos paralelismo
# Para usar múltiples núcleos
```

#### Tabla resumen

| Aspecto | Concurrencia (nuestro) | Paralelismo (no usado) |
|---------|------------------------|------------------------|
| **Threads/Procesos** | 1 thread | Múltiples threads/procesos |
| **Ejecución** | Intercalada | Simultánea real |
| **Ideal para** | I/O-bound | CPU-bound |
| **Implementación** | `asyncio` | `multiprocessing`, `threading` |
| **Complejidad** | Baja | Alta (race conditions) |
| **Overhead** | Muy bajo | Alto (context switches) |

---

### 19. ¿Qué es el "event loop" exactamente? ¿Cómo funciona internamente?

**Respuesta**:

El **event loop** es el scheduler que coordina todas las coroutines. Es un bucle infinito que:

#### Pseudocódigo del event loop
```python
# Simplificación conceptual
class EventLoop:
    def __init__(self):
        self.ready_queue = []      # Tareas listas para ejecutar
        self.io_waiting = {}       # Tareas esperando I/O
        self.selector = Selector()  # Monitorea file descriptors
    
    def run_forever(self):
        while True:
            # 1. Ejecutar tareas listas
            while self.ready_queue:
                task = self.ready_queue.pop(0)
                task.run_until_next_await()  # Ejecuta hasta el próximo await
            
            # 2. Revisar qué I/O está listo
            ready_fds = self.selector.select(timeout=0.1)
            
            # 3. Mover tareas con I/O listo a ready_queue
            for fd in ready_fds:
                task = self.io_waiting.pop(fd)
                self.ready_queue.append(task)
            
            # 4. Si no hay nada que hacer, esperar eventos I/O
            if not self.ready_queue:
                ready_fds = self.selector.select(timeout=None)  # Bloquea
```

#### Ejemplo concreto

```python
# Tienes 3 clientes conectados
async def client1():
    data = await reader.readline()  # ← Espera I/O (socket #5)
    process(data)

async def client2():
    response = await llm_generate()  # ← Espera I/O (HTTP socket #7)
    return response

async def client3():
    result = compute()  # ← CPU, no espera
    return result
```

**Estado del event loop**:
```
Iteración 1:
  ready_queue: [client3]
  io_waiting: {5: client1, 7: client2}
  
  → Ejecuta client3 (computa)
  → Termina
  → ready_queue vacía
  
  → select() revisa sockets: ninguno listo
  → Espera...

Iteración 2:
  select() detecta: socket #5 tiene datos
  
  → Mueve client1 a ready_queue
  → ready_queue: [client1]
  → Ejecuta client1 hasta process(data)
  → Si process tiene await, vuelve a io_waiting
  → Si no, termina

Iteración 3:
  select() detecta: socket #7 tiene respuesta HTTP
  
  → Mueve client2 a ready_queue
  → Ejecuta hasta return response
  → Termina
```

#### Integración con el OS

```python
# Event loop usa select/epoll/kqueue del OS
import select

# Registra sockets para monitorear
selector.register(socket_fd, EVENT_READ, callback)

# OS notifica cuando hay datos
ready = selector.select(timeout=1.0)
# → Retorna lista de file descriptors listos
```

**Ventaja**: El event loop NO hace polling activo. Usa llamadas del sistema operativo que bloquean eficientemente hasta que hay eventos.

---

### 20. ¿Cuáles son las operaciones admitidas y limitaciones del sistema?

**Respuesta**:

#### ✅ Operaciones Admitidas (10 características clave)

**1. Conversaciones simultáneas con aislamiento de estado**
```python
# Cada usuario tiene su propio:
user = f"Usuario-{next(USER_SEQ)}"         # ID único
limiter = SlidingWindowLimiter(...)         # Rate limiter exclusivo
_histories[conversation_id] = [...]         # Historial aislado
```

**2. Limitación de velocidad configurable**
```python
# En .env:
RATE_MAX_MESSAGES=10        # Mensajes permitidos
RATE_WINDOW_SECONDS=60      # En esta ventana de tiempo

# Si el usuario excede el límite:
if not limiter.allow():
    return "Demasiados mensajes. Esperá unos segundos."
```

**3. Control de contrapresión global**
```python
SEM_GLOBAL = asyncio.Semaphore(settings.MAX_IN_FLIGHT)

# Solo N llamadas simultáneas al LLM
async with SEM_GLOBAL:
    llm_reply = await llm_generate(...)
```

**4. Reintentos con backoff exponencial**
```python
for attempt in range(1, MAX_RETRIES + 1):
    try:
        resp = await client.post(...)
        if resp.status_code == 429:  # Too Many Requests
            wait = BACKOFF_INITIAL * (2 ** (attempt - 1))
            await asyncio.sleep(wait)  # 2s, 4s, 8s, 16s...
            continue
    except httpx.RequestError:
        continue
```

**5. Ajuste de ventana de tokens**
```python
def build_messages(system_prompt, history, user_text):
    budget = LLM_INPUT_TOKEN_BUDGET  # Ej: 2000 tokens
    
    # Incluir solo mensajes que quepan en el budget
    picked = []
    for msg in reversed(history):
        tokens = estimate_tokens(msg)
        if total + tokens > budget:
            break  # No cabe más
        picked.append(msg)
    
    return [system_msg] + picked + [user_msg]
```

**6. Degradación controlada sin API**
```python
if not settings.GROQ_API_KEY:
    # Modo offline con respuesta por defecto
    return "Estoy aquí para acompañarte. Probá respirar suave..."
```

**7. Conectividad dual (WebSocket + TCP)**
```python
# Opción A: Navegador → WebSocket → Gateway → TCP → Servidor
ws://localhost:8765

# Opción B: Cliente nativo → TCP directo → Servidor
telnet localhost 5001
```

**8. Trace ID para depuración**
```python
trace_id = f"{user}:m{msg_counter}"

log.info(f"[{trace_id}] → LLM start")
# Header HTTP:
headers["X-Request-ID"] = trace_id
log.info(f"[{trace_id}] ← LLM ok ({dt_ms:.0f} ms)")

# Permite correlacionar toda la request end-to-end
```

**9. Observabilidad completa**
```python
# Logs estructurados con contexto
log.info(f"[{user}] Conexión desde {peer}")
log.info(f"[{trace_id}] POST {url} model={model}")
log.warning(f"[{user}] Rate limit excedido")
log.error(f"[{trace_id}] Groq error: {e}")

# Métricas disponibles:
# - Latencia del LLM
# - Tasa de rate limiting
# - Conexiones activas
# - Errores por tipo
```

**10. Containerización completa**
```yaml
# docker-compose.yml
services:
  app:      # Servidor TCP
  gateway:  # Gateway WebSocket

# Un solo comando:
docker-compose up -d
```

---

#### ⚠️ Limitaciones Conocidas (7 limitaciones por diseño)

**1. Historial en RAM (no persistente)**
```python
_histories: dict[str, list[dict]] = defaultdict(list)
# ❌ Se pierde al reiniciar
# ✅ Migración futura: PostgreSQL/MongoDB
```

**Por qué es así**: Prototipo educativo. Más simple de entender y suficiente para demo.

**2. Sin autenticación**
```python
user = f"Usuario-{next(USER_SEQ)}"
# ❌ Cualquiera puede conectarse
# ❌ No hay verificación de identidad
# ✅ Migración futura: JWT tokens + OAuth2
```

**3. Sin persistencia de conversaciones**
```python
# ❌ No se guarda en DB
# ❌ No se puede recuperar sesión anterior
# ✅ Migración futura: 
#    CREATE TABLE messages (user_id, content, timestamp)
```

**4. Instancia única (no escalable horizontalmente)**
```python
# ❌ Un solo servidor
# ❌ Si se cae, todo se cae
# ❌ No se puede distribuir carga

# ✅ Migración futura:
#    - Redis para estado compartido
#    - Load Balancer con múltiples instancias
#    - Session affinity o state replication
```

**5. Sin cifrado**
```python
# ❌ HTTP plano (no HTTPS)
# ❌ WebSocket plano (no WSS)
# ❌ Datos visibles en la red

# ✅ Migración futura:
#    - Certificados SSL/TLS
#    - nginx como reverse proxy con HTTPS
#    - wss:// en vez de ws://
```

**6. Identificación temporal**
```python
user = f"Usuario-{next(USER_SEQ)}"
# ❌ Solo válido mientras dura la conexión
# ❌ Usuario-1 hoy ≠ Usuario-1 mañana

# ✅ Migración futura:
#    - UUID persistente
#    - user_id en DB
```

**7. Sin recuperación de sesión**
```python
# ❌ Si el cliente se desconecta:
#    - Pierde su Usuario-N
#    - Pierde su historial
#    - No puede reconectar a la misma sesión

# ✅ Migración futura:
#    - Session tokens
#    - async def reconnect(token)
#    - Recuperar historial de DB
```

---

#### Tabla Comparativa

| Aspecto | Estado Actual | Producción Requeriría |
|---------|---------------|----------------------|
| **Estado** | RAM volátil | Redis/DB persistente |
| **Autenticación** | Ninguna | JWT + OAuth2 |
| **Cifrado** | HTTP plano | TLS/SSL |
| **Escalado** | Vertical only | Horizontal + LB |
| **Observabilidad** | Logs básicos | Prometheus + Grafana |
| **Alta disponibilidad** | No | Multi-región + failover |
| **Backup** | No | Snapshots + replicación |

---

#### Justificación de las Limitaciones

**¿Por qué no implementamos todo desde el inicio?**

1. **Objetivo educativo**: Prioridad es entender conceptos (sockets, asyncio, concurrencia)
2. **Simplicidad**: Menos código = más fácil de entender y defender
3. **Tiempo de desarrollo**: Proyecto funcional en tiempo razonable
4. **Suficiencia**: Cumple los requisitos académicos
5. **Extensibilidad**: Arquitectura preparada para agregar features

**El profesor valorará**:
- ✅ Que entiendas las limitaciones
- ✅ Que puedas justificarlas
- ✅ Que sepas cómo resolverlas

**No está mal tener limitaciones en un prototipo**. Está mal **no conocerlas** o **no saber cómo superarlas**.

---

### 21. ¿Cómo prueban que el sistema realmente maneja múltiples usuarios?

**Respuesta**:

Podemos demostrarlo con **pruebas de carga** y **logs estructurados**:

#### 1. Test manual con múltiples navegadores
```bash
# Terminal 1: Levantar el sistema
docker-compose up

# Navegador 1: http://localhost:8000/client_web.html
# Navegador 2: http://localhost:8000/client_web.html (otra pestaña)
# Navegador 3: http://localhost:8000/client_web.html (otra pestaña)

# Los tres pueden enviar mensajes simultáneamente
# Los logs mostrarán:
[Usuario-1] Conexión desde ('127.0.0.1', 50234)
[Usuario-2] Conexión desde ('127.0.0.1', 50235)
[Usuario-3] Conexión desde ('127.0.0.1', 50236)
```

#### 2. Script de prueba de carga
```python
# load_test.py
import asyncio
import websockets

async def client(client_id, num_messages):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as ws:
        # Recibir saludo
        greeting = await ws.recv()
        print(f"Cliente-{client_id}: {greeting}")
        
        # Enviar mensajes
        for i in range(num_messages):
            await ws.send(f"Cliente-{client_id}: Mensaje {i}")
            response = await ws.recv()
            print(f"Cliente-{client_id} recibió: {response[:50]}...")
            await asyncio.sleep(0.5)

async def main():
    # Crear 100 clientes simultáneos
    tasks = [client(i, 5) for i in range(100)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

**Ejecutar**:
```bash
python load_test.py

# Output esperado:
Cliente-0: Usuario-1 conectado...
Cliente-1: Usuario-2 conectado...
Cliente-2: Usuario-3 conectado...
...
Cliente-99: Usuario-100 conectado...

# Los 100 pueden enviar/recibir simultáneamente
```

#### 3. Verificación en logs
```bash
docker-compose logs -f app | grep "Conexión desde"

# Verás múltiples conexiones activas:
[Usuario-1] Conexión desde ('172.18.0.1', 50234)
[Usuario-1:m1] → LLM start (len=25)
[Usuario-2] Conexión desde ('172.18.0.1', 50235)
[Usuario-2:m1] → LLM start (len=30)
[Usuario-1:m1] ← LLM ok (150 chars) 892 ms
[Usuario-3] Conexión desde ('172.18.0.1', 50236)
[Usuario-2:m1] ← LLM ok (180 chars) 1105 ms
[Usuario-3:m1] → LLM start (len=22)

# Las operaciones se intercalan = concurrencia real
```

#### 4. Métricas del sistema
```bash
# Ver cuántas conexiones TCP están activas
docker-compose exec app netstat -ant | grep 5001

# Output:
tcp  0  0  172.18.0.2:5001  172.18.0.1:50234  ESTABLISHED
tcp  0  0  172.18.0.2:5001  172.18.0.1:50235  ESTABLISHED
tcp  0  0  172.18.0.2:5001  172.18.0.1:50236  ESTABLISHED
# → 3 conexiones activas simultáneas
```

#### 5. Test con telnet
```bash
# Terminal 1
telnet localhost 5001
> Hola, soy el usuario 1

# Terminal 2 (mientras el 1 espera respuesta)
telnet localhost 5001
> Hola, soy el usuario 2

# Terminal 3
telnet localhost 5001
> Hola, soy el usuario 3

# Los tres obtienen respuestas sin bloquearse entre sí
```

**Prueba definitiva**: Simular un usuario "lento":
```python
# Cliente que tarda mucho en leer
async def slow_client():
    async with websockets.connect(uri) as ws:
        await ws.send("Mensaje 1")
        await asyncio.sleep(60)  # Espera 60 segundos sin leer
        response = await ws.recv()

# Mientras tanto, otros 100 clientes funcionan normalmente
# → Demuestra que un cliente lento NO bloquea a los demás
```

---

## Conclusión

Este proyecto demuestra conocimiento profundo de:

✅ **Networking**: Sockets, TCP, WebSocket  
✅ **Concurrencia**: AsyncIO, event loop, coroutines  
✅ **Arquitectura**: Separation of concerns, layered architecture  
✅ **Observabilidad**: Logging, tracing, métricas  
✅ **DevOps**: Docker, containerización, orquestación  
✅ **Resiliencia**: Timeouts, reintentos, rate limiting  
✅ **Integración**: APIs REST, HTTP async, manejo de errores  

El sistema es **funcional**, **escalable** y **mantenible**, con decisiones técnicas bien justificadas y código limpio y documentado.

---

---

## 📚 RESUMEN EJECUTIVO PARA LA DEFENSA

### ✅ Lo que el Sistema PUEDE hacer

| Característica | Implementación | Dónde está |
|----------------|----------------|------------|
| **Múltiples usuarios simultáneos** | Coroutine por cliente | `client_handler.py` |
| **Rate limiting por usuario** | Ventana deslizante | `rate_limiter.py` |
| **Control de concurrencia LLM** | Semáforo global | `SEM_GLOBAL` en `client_handler.py` |
| **Reintentos automáticos** | Backoff exponencial | `llm_client.py` |
| **Ventana de tokens adaptativa** | Budget + sliding window | `build_messages()` en `llm_client.py` |
| **Fallback sin API** | Respuesta por defecto | `llm_generate()` cuando no hay API key |
| **WebSocket + TCP** | Gateway + Servidor | `ws_gateway.py` + `server.py` |
| **Trazabilidad completa** | trace_id: Usuario-N:mM | Logs en todos los módulos |
| **Logs estructurados** | Niveles + formato | `logger.py` |
| **Containerización** | Docker Compose | `docker-compose.yml` |

### ⚠️ Lo que el Sistema NO puede hacer (por diseño)

| Limitación | Motivo | Solución futura |
|------------|--------|-----------------|
| **Persistencia de historial** | RAM volátil | PostgreSQL/MongoDB |
| **Autenticación de usuarios** | Sin sistema de cuentas | JWT + OAuth2 |
| **Cifrado TLS/SSL** | HTTP/WS plano | Certificados + nginx |
| **Escalado horizontal** | Estado en RAM local | Redis + Load Balancer |
| **Recuperación de sesión** | ID temporal | Tokens persistentes |
| **Multi-región** | Instancia única | Deploy distribuido |

### Conceptos Clave que DEBES dominar

#### 🔌 SOCKET
**Qué es**: Punto final de comunicación en red (IP + puerto)  
**Dónde está**: `app/server.py` (línea con `asyncio.start_server`)  
**Cómo funciona**: Se crea con `socket()`, se asocia con `bind()`, escucha con `listen()`, acepta con `accept()`

#### 🌐 TCP
**Qué es**: Protocolo confiable que garantiza orden y entrega  
**Por qué orden**: Números de secuencia + reordenamiento en receptor  
**Ventaja**: No tenemos que preocuparnos por paquetes perdidos o desordenados

#### ⚡ ASYNCIO
**Qué es**: Concurrencia cooperativa sin hilos  
**Por qué usarlo**: I/O-bound (esperamos red), miles de coroutines con 1 hilo  
**Alternativa**: Hilos = 8MB cada uno, máximo 1000 clientes

#### 🔄 CONCURRENCIA vs PARALELISMO
**Concurrencia** (nuestro caso): 1 CPU, múltiples tareas intercaladas  
**Paralelismo** (NO usamos): Múltiples CPUs, ejecución simultánea real  
**Por qué concurrencia**: Nuestro código espera 95% del tiempo (I/O-bound)

#### 🚦 NIVEL DE CONCURRENCIA
1. **Conexiones**: Ilimitadas (limitado por SO)
2. **LLM simultáneos**: Limitado por semáforo (`MAX_IN_FLIGHT`)
3. **Mensajes/usuario**: Limitado por rate limiter (10 msg/60s)

#### 👥 MULTIUSUARIO
**Cómo identificamos**: `Usuario-N` (contador secuencial)  
**Cómo aislamos**: Cada cliente tiene su socket, rate limiter e historial  
**Clave única**: `conversation_id` para el historial en RAM

#### 📊 OBSERVABILIDAD
**Logs**: Niveles (debug, info, warning, error)  
**Trazabilidad**: `trace_id` = `Usuario-N:mM` vincula todas las operaciones  
**Métricas**: Latencia LLM, rate limiting, errores

#### 🐳 DOCKER
**Por qué**: Reproducibilidad + aislamiento + portabilidad  
**Arquitectura**: `app` (servidor TCP) + `gateway` (WebSocket)  
**Red interna**: Los contenedores se comunican por nombre de servicio

### Flujo Completo del Sistema

```
1. Usuario escribe en navegador
   ↓
2. JavaScript envía por WebSocket al gateway (puerto 8765)
   ↓
3. Gateway abre conexión TCP al servidor (puerto 5001)
   ↓
4. Servidor crea coroutine handle_client()
   ↓
5. Se asigna Usuario-N
   ↓
6. Se valida rate limit
   ↓
7. Semáforo limita concurrencia al LLM
   ↓
8. llm_client hace POST HTTP a Groq
   ↓
9. Se guarda en historial (RAM)
   ↓
10. Respuesta vuelve por el mismo camino
   ↓
11. Usuario ve mensaje en navegador
```

### Dónde está cada cosa en el código

| Concepto | Archivo | Línea aproximada |
|----------|---------|------------------|
| Socket de escucha | `app/server.py` | `asyncio.start_server(...)` |
| Manejo de cliente | `app/client_handler.py` | `async def handle_client(...)` |
| Rate limiting | `app/utils/rate_limiter.py` | `class SlidingWindowLimiter` |
| Semáforo | `app/client_handler.py` | `SEM_GLOBAL = asyncio.Semaphore(...)` |
| Historial | `app/services/llm_client.py` | `_histories: dict[str, list[dict]]` |
| Gateway WS↔TCP | `gateway/ws_gateway.py` | `async def bridge_ws_to_tcp(...)` |
| Event loop | `app/server.py` | `asyncio.run(main())` |
| Logs | `app/utils/logger.py` | `get_logger(...)` |

### Preguntas que el profesor DEFINITIVAMENTE hará

1. ✅ **"Explicame cómo funciona el servidor"**  
   → Ver sección "¿Cómo funciona el servidor?" (pregunta 1)

2. ✅ **"¿Cómo distinguís quién es cada usuario?"**  
   → `Usuario-N` secuencial + socket único + historial por `conversation_id`

3. ✅ **"¿Qué pasa si dos usuarios envían mensaje al mismo tiempo?"**  
   → Están aislados, cada uno tiene su coroutine independiente

4. ✅ **"Explicame qué es un socket"**  
   → Punto final de comunicación, IP + puerto, analogía: número de teléfono

5. ✅ **"¿Por qué usaron asyncio en vez de hilos?"**  
   → I/O-bound, miles de coroutines vs 1000 hilos, menos memoria

6. ✅ **"¿Cómo llegan los mensajes en orden?"**  
   → TCP garantiza con números de secuencia + reordenamiento

7. ✅ **"Mostrá dónde está el socket en el código"**  
   → `app/server.py`: `asyncio.start_server()`

8. ✅ **"Explicame Docker"**  
   → Reproducibilidad, aislamiento, `docker-compose up` y funciona

9. ✅ **"¿Qué es concurrencia?"**  
   → Múltiples tareas progresando intercalándose (1 CPU)

10. ✅ **"Simulemos que se cae la red"**  
    → `docker-compose stop app` → gateway notifica error al cliente

### Respuestas cortas para preguntas rápidas

**¿Qué es TCP?** → Protocolo confiable con orden garantizado  
**¿Qué es un socket?** → Punto final de comunicación (IP + puerto)  
**¿Qué es asyncio?** → Concurrencia cooperativa sin hilos  
**¿Qué es un hilo?** → Unidad de ejecución, ~8MB cada uno  
**¿Qué es concurrencia?** → Múltiples tareas intercalándose  
**¿Qué es paralelismo?** → Ejecución simultánea real (múltiples CPUs)  
**¿Nivel de concurrencia?** → Conexiones ilimitadas, LLM limitado por semáforo  
**¿Multiusuario cómo?** → Una coroutine por cliente, aislamiento total  
**¿Observabilidad?** → Logs estructurados + trace_id + métricas  
**¿Por qué Docker?** → Reproducibilidad y aislamiento  
**¿Por qué gateway?** → Navegadores no hablan TCP, solo WebSocket  
**¿Historial dónde?** → RAM (dict con conversation_id como clave)  

### Tips para la Defensa

1. **Siempre menciona el trace_id**: Demuestra que entendés observabilidad
2. **Relaciona conceptos**: "El socket es no bloqueante gracias a asyncio"
3. **Usa analogías**: Socket = teléfono, Event loop = director de orquesta
4. **Mostrar logs reales**: Abrí `docker-compose logs -f` durante la demo
5. **Demos en vivo**: Abrí múltiples pestañas del navegador para mostrar multiusuario
6. **Código específico**: No digas "en el código", decí "en app/server.py línea 15"
7. **Justifica decisiones**: No digas "usamos asyncio", decí "usamos asyncio porque..."

### Posibles Simulaciones del Profesor

**Simulación 1: Desconexión de red**
```bash
# El profesor puede pedir:
docker-compose stop app
# → Gateway detecta, cierra WebSocket, cliente ve error
```

**Simulación 2: Sobrecarga del sistema**
```bash
# Muchos usuarios simultáneos
# → Rate limiter bloquea flooding
# → Semáforo limita llamadas al LLM
# → Sistema se mantiene estable
```

**Simulación 3: Cliente lento**
```bash
# Un cliente tarda en leer
# → NO bloquea a otros clientes
# → writer.drain() implementa backpressure
```

---

## Checklist Final Pre-Defensa

### Conceptos Fundamentales
- [ ] He leído todo el documento DEFENSA_PROYECTO.md
- [ ] Puedo explicar qué es un socket sin mirar apuntes
- [ ] Puedo explicar la diferencia entre concurrencia y paralelismo
- [ ] Sé dónde está el socket en el código (`app/server.py`)
- [ ] Entiendo por qué usamos asyncio (I/O-bound)
- [ ] Puedo explicar cómo identificamos usuarios (Usuario-N)
- [ ] Entiendo el flujo completo (navegador → gateway → servidor → LLM)
- [ ] Sé qué es el event loop conceptualmente
- [ ] Entiendo cómo TCP garantiza orden (números de secuencia)
- [ ] Puedo justificar Docker (reproducibilidad + aislamiento)

### Implementación Específica
- [ ] Sé cómo funciona el rate limiter (ventana deslizante)
- [ ] Entiendo el semáforo (limita concurrencia al LLM)
- [ ] Puedo explicar qué hace `writer.drain()`
- [ ] Conozco la función del trace_id (Usuario-N:mM)
- [ ] Entiendo el ajuste de ventana de tokens
- [ ] Sé cómo funcionan los reintentos con backoff exponencial

### Operaciones y Limitaciones
- [ ] Puedo listar las 10 operaciones admitidas del sistema
- [ ] Puedo explicar las 7 limitaciones conocidas
- [ ] Sé justificar por qué tenemos esas limitaciones
- [ ] Puedo explicar cómo resolver cada limitación en producción
- [ ] Entiendo la diferencia entre prototipo educativo y sistema productivo

### Demos y Pruebas
- [ ] Puedo mostrar logs en vivo con `docker-compose logs -f`
- [ ] He probado el sistema con múltiples navegadores abiertos
- [ ] Sé ejecutar el script de carga (`load_test.py` conceptual)
- [ ] Puedo demostrar el rate limiting en acción
- [ ] Sé simular una desconexión de red con Docker

### Preguntas Críticas del Profesor
- [ ] Puedo responder "¿Cómo funciona el servidor?" (pregunta 1)
- [ ] Puedo responder "¿Cómo distinguís usuarios?" (identificación)
- [ ] Puedo responder "¿Por qué asyncio?" (justificación técnica)
- [ ] Puedo responder "¿Qué pasa si dos usuarios escriben juntos?" (aislamiento)
- [ ] Puedo responder "¿Cuáles son las limitaciones?" (pregunta 20)
- [ ] Puedo responder sobre simulación de red (Docker + tc)

---

**Autor**: Máximo Catalán  
**Fecha**: Noviembre 2025  
**Repositorio**: [PsicoIA](https://github.com/Catalan-Maximo/PsicoIA)

---

## 🎯 Última Recomendación

**PRACTICA explicando en voz alta** cada sección. Si podés explicarlo sin mirar, lo dominás. Si dudás, releé esa parte hasta que sea natural.

**¡Mucha suerte en la defensa! 🚀**
