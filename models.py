from dataclasses import dataclass
from typing import Optional

@dataclass
class Event:
    timestamp: float
    source: str
    value: float = 1.0

@dataclass
class Burst:
    start: float
    end: Optional[float]
    total_events: int
    peak_rate: float