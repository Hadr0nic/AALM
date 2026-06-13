from app.db import get_conn
from app.realtime import hub
import asyncio
import time


class InMemoryStorage:
    def add_event(self, event):
        # Save to database
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO events (timestamp, source, value) VALUES (?, ?, ?)",
                (event.timestamp, event.source, event.value)
            )
            conn.commit()

        # Safe broadcast from background thread
        self._broadcast_event(event)

    def _broadcast_event(self, event):
        """Thread-safe broadcast"""
        if hub.main_loop is None:
            print("Warning: Main loop not set yet")
            return

        try:
            asyncio.run_coroutine_threadsafe(
                hub.broadcast({
                    "type": "event",
                    "timestamp": event.timestamp,
                    "value": event.value
                }),
                hub.main_loop
            )
        except Exception as e:
            print("Broadcast failed:", e)

    def get_events(self, window_seconds=60):
        now = time.time()
        with get_conn() as conn:
            cur = conn.execute(
                """
                SELECT timestamp, value
                FROM events
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
                """,
                (now - window_seconds,)
            )
            return cur.fetchall()

    def get_bursts(self):
        with get_conn() as conn:
            cur = conn.execute(
                "SELECT start, end, peak, total_events FROM bursts ORDER BY start DESC"
            )
            return cur.fetchall()


storage = InMemoryStorage()