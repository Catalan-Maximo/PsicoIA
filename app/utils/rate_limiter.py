"""
Implementación de un limitador de tasa basado en una ventana deslizante.

- Permite controlar la cantidad de eventos que pueden ocurrir en un intervalo de tiempo definido.
- Utiliza una cola (deque) para almacenar marcas de tiempo de los eventos recientes.
"""

import time  # Para obtener marcas de tiempo monotónicas
from collections import deque  # Cola eficiente para manejar eventos recientes

class SlidingWindowLimiter:
    def __init__(self, max_events: int, window_seconds: int):
        """
        Inicializa el limitador de tasa con una ventana deslizante.

        - `max_events`: Número máximo de eventos permitidos dentro de la ventana.
        - `window_seconds`: Duración de la ventana de tiempo en segundos.
        """
        self.max = max_events  # Límite de eventos permitidos
        self.win = window_seconds  # Duración de la ventana en segundos
        self.events = deque()  # Cola para almacenar marcas de tiempo de eventos

    def allow(self) -> bool:
        """
        Determina si se permite un nuevo evento basado en la ventana deslizante.

        - Elimina eventos antiguos que están fuera de la ventana de tiempo.
        - Si el número de eventos recientes está por debajo del límite, permite el nuevo evento.
        - Devuelve `True` si el evento es permitido, `False` en caso contrario.
        """
        now = time.monotonic()  # Marca de tiempo actual (monotónica para evitar retrocesos)
        # Eliminar eventos fuera de la ventana de tiempo
        while self.events and now - self.events[0] > self.win:
            self.events.popleft()
        # Verificar si se puede permitir un nuevo evento
        if len(self.events) < self.max:
            self.events.append(now)  # Registrar el nuevo evento
            return True
        return False  # Rechazar el evento si se excede el límite
