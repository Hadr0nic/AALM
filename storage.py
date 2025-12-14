from collections import deque
from AALM.models import Event, Burst

class InMemoryStorage:
    def __init__(self, max_events: int):
        self.events = deque(maxlen=max_events)
        self.bursts: list[Burst] = []

    def add_event(self, event: Event):
        self.events.append(event)

    def add_burst(self, burst: Burst):
        self.bursts.append(burst)