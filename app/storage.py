from app.db import get_conn

class InMemoryStorage:
    def add_event(self, event):
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO events (timestamp, source, value) VALUES (?, ?, ?)",
                (event.timestamp, event.source, event.value)
            )
            conn.commit()

    def add_burst(self, burst):
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO bursts (start, end, peak, total_events) VALUES (?, ?, ?, ?)",
                (burst.start, burst.end, burst.peak_rate, burst.total_events)
            )
            conn.commit()

    def get_events(self, limit=1000):
        with get_conn() as conn:
            cur = conn.execute(
                "SELECT timestamp, source, value FROM events ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            
    def get_events(self, window_seconds=60):
        import time
        now = time.time()

        with get_conn() as conn:
            cur = conn.execute(
                """
                SELECT timestamp, value
                FROM events
                WHERE timestamp >= ?
                """,
                (now - window_seconds,)
            )
            return cur.fetchall()
        

    def get_bursts(self):
        with get_conn() as conn:
            cur = conn.execute(
                "SELECT start, end, peak, total_events FROM bursts"
            )
            return cur.fetchall()
            
            
storage = InMemoryStorage()
