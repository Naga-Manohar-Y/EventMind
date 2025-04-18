#src/storage/database.py
import sqlite3
import os
import time


DB_PATH = "data/events.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Check if events table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
    if not c.fetchone():
        # Create table and indexes only if it doesn't exist
        c.execute("""
        CREATE TABLE events (
            id TEXT PRIMARY KEY,
            name TEXT,
            url TEXT,
            start_utc TEXT,
            city TEXT,
            country TEXT,
            is_free INTEGER,
            venue_name TEXT,
            category_name TEXT,
            summary TEXT,
            lead_score INTEGER
        )
        """)
        c.execute("CREATE INDEX idx_events_city ON events (city)")
        c.execute("CREATE INDEX idx_events_start ON events (start_utc)")
        c.execute("CREATE INDEX idx_events_score ON events (lead_score)")
    conn.commit()
    conn.close()

def save_event(event: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # Check if event exists
        c.execute("SELECT id FROM events WHERE id = ?", (event["id"],))
        if c.fetchone():
            print(f"ℹ️ Skipped event {event['id']}: Already exists")
            return
        # Insert new event
        c.execute("""
        INSERT OR REPLACE INTO events (
            id, name, url, start_utc, city, country, is_free, venue_name, category_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event["id"],
            event["name"],
            event["url"],
            event["start_utc"],
            event.get("city", ""),
            event.get("country", ""),
            event["is_free"],
            event.get("venue_name", ""),
            event.get("category_name", "")
        ))
        conn.commit()
        print(f"✅ Stored: {event['name']}")
    except sqlite3.Error as e:
        print(f"❌ Failed to save event {event.get('id', 'unknown')}: {e}")
    finally:
        conn.close()

def update_event_summary(event_id: str, summary: str):
    for _ in range(3):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE events SET summary = ? WHERE id = ?", (summary, event_id))
            conn.commit()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(0.1)
            else:
                raise
        finally:
            conn.close()
            
    raise sqlite3.OperationalError("Failed to update summary after retries")