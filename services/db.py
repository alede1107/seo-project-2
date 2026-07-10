import sqlite3
import os
import datetime
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "flightscope.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)

conn.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_number TEXT NOT NULL,
        city TEXT,
        state TEXT,
        country TEXT,
        lat REAL,
        lon REAL,
        summary TEXT,
        articles_json TEXT,
        searched_at TEXT NOT NULL
    )
""")
conn.commit()

CACHE_MINUTES = 15

def get_cached_search(flight_number):
    cutoff = (datetime.datetime.now() - datetime.timedelta(minutes=CACHE_MINUTES)).isoformat()
    cursor = conn.execute(
        "SELECT * FROM searches WHERE flight_number = ? AND searched_at > ? ORDER BY searched_at DESC LIMIT 1",
        (flight_number, cutoff),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [d[0] for d in cursor.description]
    return dict(zip(columns, row))

def save_search(flight_number, destination, summary, articles):
    conn.execute(
        "INSERT INTO searches (flight_number, city, state, country, lat, lon, summary, articles_json, searched_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            flight_number,
            destination["city"],
            destination["state"],
            destination["country"],
            destination["lat"],
            destination["lon"],
            summary,
            json.dumps(articles),
            datetime.datetime.now().isoformat(),
        ),
    )
    conn.commit()