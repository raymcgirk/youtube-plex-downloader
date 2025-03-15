import json
import logging
import os
import threading

cache_lock = threading.Lock()  # Prevent multiple processes from corrupting the cache


def load_cache(cache_file):
    """Loads the cache from file, handling JSON errors and empty files gracefully."""
    try:
        if os.path.exists(cache_file) and os.path.getsize(cache_file) == 0:
            return {}  # Avoid JSON errors for empty files
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_cache(cache, cache_file, finalize=True):
    """Saves the cache incrementally to prevent loss of metadata."""
    with cache_lock:
        try:
            # Load existing cache to avoid overwriting old data
            existing_cache = load_cache(cache_file)

            # Merge new data with the existing cache
            for channel, videos in cache.items():
                if channel not in existing_cache:
                    existing_cache[channel] = []
                for video in videos:
                    if video["url"] not in [v["url"] for v in existing_cache[channel]]:
                        existing_cache[channel].append(video)

            # Write updated cache back to file
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(existing_cache, f, indent=4)

            if finalize:
                logging.info("✅ Metadata cache successfully updated.")

        except Exception as e:
            logging.error(f"⚠ Failed to save cache: {str(e)}")
