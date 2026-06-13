from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio

from app.models import Event
from app.storage import storage
from app.config import WINDOW_SIZE
from app.schemas import EventIn, SummaryOut
from app.db import init_db
from app.background import start_background_threads

app = FastAPI(title="Adaptive Activity & Load Monitor")

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)


# Startup
init_db()

@app.on_event("startup")
def startup_event():
    start_background_threads()
    # Register main loop for thread-safe broadcasting
    hub.set_main_loop(asyncio.get_running_loop())


# Frontend
@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"ok": True}



# API
from app.realtime import hub
import time

@app.post("/event")
async def ingest_event(event: EventIn):
    e = Event(**event.dict())
    storage.add_event(e)

    # 🔥 immediate push
    await hub.broadcast({
        "type": "event",
        "timestamp": e.timestamp,
        "value": e.value
    })

    return {"status": "ok"}


@app.get("/summary", response_model=SummaryOut)
def summary():

    bursts = storage.get_bursts()
    events = storage.get_events(10_000_000)

    if not bursts:
        return SummaryOut(
            total_events=len(events),
            burst_count=0,
            avg_burst_duration=0,
            max_peak_rate=0
        )

    durations = [
        burst[1] - burst[0]
        for burst in bursts
        if burst[1] is not None
    ]

    return SummaryOut(
        total_events=len(events),
        burst_count=len(bursts),
        avg_burst_duration=(
            sum(durations) / len(durations)
            if durations else 0
        ),
        max_peak_rate=max(
            burst[2]
            for burst in bursts
        )
    )



# WebSocket
from app.realtime import hub

@app.websocket("/ws/events")
async def ws_events(ws: WebSocket):
    print("WS HANDLER ENTERED")
    await ws.accept()
    await hub.connect(ws)

    try:
        while True:
            await asyncio.sleep(60)  # keep-alive only

    finally:
        await hub.disconnect(ws)
