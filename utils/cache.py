import json
import os
import threading
import sqlite3

cache_lock = threading.Lock()  # Prevent multiple processes from corrupting the cache
DB_FILE = "video_tracking.db"  # SQLite database for long-term tracking

# Ensure SQLite DB is initialized
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS last_downloaded (
                channel TEXT PRIMARY KEY,
                last_video_url TEXT,
                last_upload_date TEXT
            )
        """
        )
        conn.commit()

init_db()

# SQLite helper functions
def get_last_downloaded(channel):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_upload_date FROM last_downloaded WHERE channel = ?", (channel,))
        row = cursor.fetchone()
        return row[0] if row else None

def update_last_downloaded(channel, video_url, upload_date):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "REPLACE INTO last_downloaded (channel, last_video_url, last_upload_date) VALUES (?, ?, ?)",
            (channel, video_url, upload_date)
        )
        conn.commit()

# JSON Cache Management
def load_cache(cache_file):
    """Loads the cache from file, handling JSON errors and empty files gracefully."""
    try:
        if os.path.exists(cache_file) and os.path.getsize(cache_file) == 0:
            return {}  # Avoid JSON errors for empty files
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_cache(cache, cache_file, last_processed_video=None, channel=None, finalize=False):
    """Efficiently updates the cache, preventing race conditions and corruption."""

    existing_cache = load_cache(cache_file)

    with cache_lock:  # Lock only during write operations
        if existing_cache and cache:
            existing_cache.update(cache)

        if last_processed_video and channel:
            existing_cache[channel + "_in_progress"] = last_processed_video["upload_date"]
            update_last_downloaded(channel, last_processed_video["url"], last_processed_video["upload_date"])

        if finalize and channel:
            existing_cache.pop(channel + "_in_progress", None)

        temp_file = cache_file + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(existing_cache, f, indent=4) #type: ignore
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_file, cache_file)  # Fully atomic on all platforms
