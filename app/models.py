from dataclasses import dataclass
from typing import Optional

''' dataclasses for internal use '''

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