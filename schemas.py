from pydantic import BaseModel

class EventIn(BaseModel):
    timestamp: float
    source: str
    value: float = 1.0  # default 1.0 if not provided

class BurstOut(BaseModel):
    start: float
    end: float
    duration: float
    total_events: int
    peak_rate: float
    anomaly_score: float

class SummaryOut(BaseModel):
    total_events: int
    burst_count: int
    avg_burst_duration: float
    max_peak_rate: float