import time
import random
import threading
import asyncio

from app.models import Event, Burst
from app.storage import storage
from app.analyzer import compute_rate, compute_threshold, BurstDetector
from app.config import WINDOW_SIZE, ANALYSIS_INTERVAL


# Global analysis state
detector = BurstDetector()
rate_history = []


# Fake event generator
from app.realtime import hub   # add this import

# Fake event generator
def fake_event_loop():
    while True:
        event = Event(
            timestamp=time.time(),
            source="simulator",
            value=random.randint(1, 5)
        )
        storage.add_event(event) 
        time.sleep(1)


# Analysis engine
def analysis_loop():
    while True:
        now = time.time()

        # fetch DB events
        events = storage.get_events(WINDOW_SIZE)

        # compute rate
        rate = compute_rate(events, now, WINDOW_SIZE)
        rate_history.append(rate)

        # threshold
        threshold = compute_threshold(rate_history)

        # burst detection
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


# Thread starter (from main)
def start_background_threads():
    threading.Thread(target=fake_event_loop, daemon=True).start()
    threading.Thread(target=analysis_loop, daemon=True).start()
