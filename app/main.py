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



# Frontend
@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"ok": True}



# API
@app.post("/event")
def ingest_event(event: EventIn):
    storage.add_event(Event(**event.dict()))
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
@app.websocket("/ws/events")
async def ws_events(ws: WebSocket):

    await ws.accept()

    last_timestamp = 0

    while True:

        events = storage.get_events(WINDOW_SIZE)

        new_events = [
            e
            for e in events
            if e[0] > last_timestamp
        ]

        if new_events:

            await ws.send_json([
                {
                    "timestamp": e[0],
                    "value": e[1]
                }
                for e in new_events
            ])

            last_timestamp = new_events[-1][0]

        await asyncio.sleep(0.5)
