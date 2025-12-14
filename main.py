from fastapi import FastAPI

import time
import asyncio, threading
from AALM.config import *
from AALM.models import Event, Burst
from AALM.storage import InMemoryStorage
from AALM.analyzer import compute_rate, compute_threshold, BurstDetector
from AALM.schemas import EventIn, BurstOut, SummaryOut


from typing import List



app = FastAPI(
    title="Adaptive Activity & Load Monitor",
)

@app.get("/")
def root():
    return {"status": "AALM running"}


@app.get("/health")
def health():
    return {"ok": True}

storage = InMemoryStorage(MAX_EVENT_HISTORY)
detector = BurstDetector()
rate_history = []

@app.post("/event")
def ingest_event(event: EventIn):
    storage.add_event(Event(**event.dict()))
    return {"status": "ok"}

@app.get("/summary", response_model=SummaryOut)
def summary():
    bursts = storage.bursts
    if not bursts:
        return SummaryOut(
            total_events=len(storage.events),
            burst_count=0,
            avg_burst_duration=0,
            max_peak_rate=0
        )

    durations = [b.end - b.start for b in bursts if b.end]
    return SummaryOut(
        total_events=len(storage.events),
        burst_count=len(bursts),
        avg_burst_duration=sum(durations) / len(durations),
        max_peak_rate=max(b.peak_rate for b in bursts)
    )



# WebSocket
from fastapi import WebSocket

@app.websocket("/ws/events")
async def ws_events(ws: WebSocket):
    await ws.accept()
    import asyncio
    last_len = 0

    while True:
        if len(storage.events) != last_len:
            new_events = list(storage.events)[last_len:]
            await ws.send_json([e.__dict__ for e in new_events])
            last_len = len(storage.events)

        await asyncio.sleep(0.5)


import random

def fake_event_loop():
    while True:
        storage.add_event(Event(
            timestamp=time.time(),
            source="simulator",
            value=random.randint(1, 5)
        ))
        time.sleep(1)

threading.Thread(target=fake_event_loop, daemon=True).start()


# background loop
import threading

def analysis_loop():
    while True:
        now = time.time()
        rate = compute_rate(storage.events, now, WINDOW_SIZE)
        rate_history.append(rate)
        threshold = compute_threshold(rate_history)

        finished = detector.update(rate, threshold, now)
        if finished:
            storage.add_burst(
                Burst(
                    start=finished["start"],
                    end=now,
                    total_events=int(finished["events"]),
                    peak_rate=finished["peak"]
                )
            )
        time.sleep(ANALYSIS_INTERVAL)

threading.Thread(target=analysis_loop, daemon=True).start()
