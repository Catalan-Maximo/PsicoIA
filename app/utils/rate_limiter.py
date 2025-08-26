import time
from collections import deque

class SlidingWindowLimiter:
    def __init__(self, max_events: int, window_seconds: int):
        self.max = max_events
        self.win = window_seconds
        self.events = deque()

    def allow(self) -> bool:
        now = time.monotonic()
        while self.events and now - self.events[0] > self.win:
            self.events.popleft()
        if len(self.events) < self.max:
            self.events.append(now)
            return True
        return False
