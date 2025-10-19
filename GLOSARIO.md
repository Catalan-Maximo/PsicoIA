# Glosario Técnico - PsicoIA

Guía de términos técnicos utilizados en el proyecto para facilitar el estudio y comprensión.

---

## A

### **Asyncio**
Biblioteca estándar de Python para programación asíncrona. Permite ejecutar código de forma no bloqueante usando coroutines y un event loop. En PsicoIA, gestiona múltiples conexiones de usuarios simultáneamente sin usar threads.

**Ejemplo**: `await reader.readline()` libera el control del event loop mientras espera datos.

### **API Key**
Clave de autenticación para acceder a servicios externos (como Groq). Se almacena en `.env` como `GROQ_API_KEY`.

### **Async/Await**
Palabras clave de Python para programación asíncrona.
- `async def`: Define una función coroutine
- `await`: Pausa la ejecución hasta que se complete una operación I/O

---

## B

### **Backoff Exponencial**
Estrategia de reintentos donde el tiempo de espera se duplica en cada intento. Ejemplo: 0.5s → 1s → 2s → 4s.

**En PsicoIA**: Implementado en `llm_client.py` para manejar errores 429 y 5xx del LLM.

### **Backpressure**
Mecanismo para evitar sobrecarga cuando el sistema recibe más requests de los que puede procesar. 

**En PsicoIA**: El semáforo `MAX_IN_FLIGHT` limita llamadas simultáneas al LLM.

### **Buffer**
Área temporal de memoria para almacenar datos. En sockets TCP, mantiene datos hasta que el receptor los procese.

---

## C

### **Concurrencia**
Capacidad de manejar múltiples tareas "al mismo tiempo". En asyncio, se logra alternando entre tareas durante operaciones de I/O.

**Diferencia con paralelismo**: Concurrencia = una CPU cambia entre tareas; Paralelismo = múltiples CPUs ejecutan simultáneamente.

### **Coroutine**
Función que puede pausar y reanudar su ejecución. Definida con `async def` en Python.

**Ejemplo en PsicoIA**: `handle_client()` es una coroutine; cada conexión obtiene su propia instancia.

### **Connection Pool**
Conjunto reutilizable de conexiones. `httpx.AsyncClient` mantiene un pool de conexiones HTTP al LLM para eficiencia.

### **Conversation ID**
Identificador único de una conversación (ej: `"Usuario-3"`). Usado para mantener historiales separados por usuario.

---

## D

### **Docker Compose**
Herramienta para definir y ejecutar aplicaciones Docker multi-contenedor mediante un archivo YAML.

**En PsicoIA**: `docker-compose.yml` define servicios `app` y `gateway`.

### **Dockerfile**
Archivo con instrucciones para construir una imagen Docker (FROM, COPY, RUN, etc.).

### **Drain**
Operación que asegura que todos los datos buffereados se envíen antes de continuar.

**Ejemplo**: `await writer.drain()` asegura que el mensaje TCP se envió completamente.

---

## E

### **Event Loop**
Motor central de asyncio que ejecuta coroutines, callbacks y maneja I/O. Es un bucle infinito que alterna entre tareas pausadas.

**En PsicoIA**: Un solo event loop maneja todas las conexiones de usuarios.

### **Environment Variables**
Variables del sistema operativo que configuran aplicaciones. PsicoIA las carga desde `.env` con `python-dotenv`.

---

## F

### **Fallback**
Comportamiento alternativo cuando falla la operación principal.

**En PsicoIA**: Si no hay API key, `llm_client.py` retorna un mensaje empático offline en lugar de fallar.

---

## G

### **Gateway**
Intermediario entre dos protocolos o sistemas.

**En PsicoIA**: `ws_gateway.py` convierte mensajes WebSocket (navegador) a TCP (servidor).

### **Graceful Degradation**
Estrategia donde el sistema continúa funcionando (con capacidad reducida) ante fallos parciales.

**Ejemplo**: Respuestas offline si el LLM no está disponible.

---

## H

### **Handshake**
Proceso inicial de establecimiento de conexión donde cliente y servidor negocian parámetros.

**WebSocket**: Cliente envía upgrade request; servidor acepta con código 101.

### **HTTP Status Codes**
Códigos numéricos de respuesta HTTP.
- `200`: OK
- `429`: Too Many Requests (rate limit)
- `5xx`: Errores del servidor

---

## I

### **I/O Bound**
Operaciones limitadas por la velocidad de entrada/salida (disco, red) en lugar de CPU.

**Por qué asyncio es ideal**: Mientras espera I/O, puede ejecutar otras tareas.

### **Idempotente**
Operación que produce el mismo resultado sin importar cuántas veces se ejecute.

**Ejemplo**: GET requests son idempotentes; POST generalmente no lo es.

---

## L

### **Latencia**
Tiempo entre enviar un request y recibir respuesta.

**En logs**: `← LLM ok (180 chars) 1234 ms` — la latencia fue 1234ms.

### **LLM (Large Language Model)**
Modelo de IA entrenado en grandes cantidades de texto para generar respuestas coherentes. Ejemplos: GPT, LLaMA, Claude.

**En PsicoIA**: Usa Groq API con modelo LLaMA 3.1.

### **Locks (asyncio.Lock)**
Primitiva de sincronización que previene race conditions al acceder datos compartidos.

**En PsicoIA**: Cada historial de conversación tiene un lock para evitar modificaciones simultáneas.

---

## M

### **Message Queue**
Cola donde se almacenan mensajes para procesamiento asíncrono. No implementada aún en PsicoIA, pero útil para escalabilidad.

### **Modelo de Actor**
Patrón donde cada "actor" (entidad) procesa mensajes de forma independiente.

**En PsicoIA**: Cada `handle_client()` es conceptualmente un actor con su propio estado.

---

## P

### **Pydantic**
Biblioteca para validación de datos y settings usando type hints de Python.

**En PsicoIA**: `config.py` usa `pydantic-settings` para validar `.env`.

### **Prompt del Sistema (System Prompt)**
Instrucciones iniciales que definen el comportamiento del LLM.

**En PsicoIA**: `SYSTEM_PROMPT` en `promptgeneral.py` define la personalidad del chatbot.

---

## R

### **Race Condition**
Error que ocurre cuando múltiples threads/coroutines acceden datos compartidos simultáneamente.

**Solución**: Locks (`asyncio.Lock`) para sincronizar acceso.

### **Rate Limiting**
Restricción de la cantidad de operaciones permitidas en un período.

**Algoritmo en PsicoIA**: Ventana deslizante (sliding window) — 6 mensajes por 10 segundos por usuario.

### **Reader/Writer (asyncio)**
Abstracciones de alto nivel para leer/escribir streams asíncronamente.

**Ejemplo**: `reader, writer = await asyncio.open_connection()`

### **Retry Logic**
Estrategia para reintentar operaciones fallidas con delays crecientes.

---

## S

### **Semaphore (asyncio.Semaphore)**
Primitiva de sincronización que limita el número de tareas que pueden ejecutarse simultáneamente.

**En PsicoIA**: `SEM_GLOBAL = asyncio.Semaphore(MAX_IN_FLIGHT)` limita requests al LLM.

### **Sliding Window**
Técnica donde se mantiene una ventana temporal móvil de eventos.

**En PsicoIA**: `rate_limiter.py` usa ventana deslizante para contar mensajes recientes.

### **Socket**
Endpoint de comunicación de red (IP + puerto). Python usa `socket` para comunicación TCP/UDP.

### **Stateless**
Diseño donde el servidor no mantiene estado de sesión entre requests.

**En PsicoIA**: Casi stateless (historial en RAM se puede mover a caché distribuida).

### **Stream**
Flujo continuo de datos. En asyncio, `StreamReader`/`StreamWriter` manejan streams TCP.

---

## T

### **TCP (Transmission Control Protocol)**
Protocolo de transporte confiable y orientado a conexión. Garantiza entrega ordenada de datos.

**Puerto en PsicoIA**: 5001

### **Timeout**
Tiempo máximo de espera antes de cancelar una operación.

**En PsicoIA**: `LLM_TIMEOUT_SECONDS` limita la espera de respuesta del LLM.

### **Token (LLM)**
Unidad básica de texto procesada por LLMs. Aproximadamente 4 caracteres en español.

**Ventana de tokens**: Límite de contexto que el modelo puede procesar (ej: 8k tokens).

### **Trace ID**
Identificador único para rastrear una operación a través de múltiples componentes.

**Formato en PsicoIA**: `Usuario-3:m5` (Usuario 3, mensaje 5).

---

## W

### **WebSocket**
Protocolo de comunicación bidireccional sobre HTTP. Mantiene conexión abierta para mensajes en tiempo real.

**Puerto en PsicoIA**: 8765  
**Formato URL**: `ws://localhost:8765` (sin TLS) o `wss://` (con TLS)

---

## Conceptos de Arquitectura

### **Microservicios**
Arquitectura donde la aplicación se divide en servicios pequeños e independientes.

**En PsicoIA**: `app` (lógica) y `gateway` (transporte) son servicios separados.

### **Separation of Concerns**
Principio de diseño donde cada módulo tiene una responsabilidad única.

**Ejemplo**: 
- `server.py`: Acepta conexiones
- `client_handler.py`: Maneja usuarios
- `llm_client.py`: Interactúa con LLM

### **Dependency Injection**
Patrón donde las dependencias se pasan desde fuera en lugar de crearlas internamente.

**Ejemplo**: `settings` se importa en lugar de leer `.env` directamente en cada módulo.

---