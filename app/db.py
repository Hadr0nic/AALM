import sqlite3
from contextlib import contextmanager

DB_PATH = "aalm.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        source TEXT,
        value REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bursts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start REAL,
        end REAL,
        peak REAL,
        total_events INTEGER
    )
    """)

    conn.commit()
    conn.close()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close() 
