import logging
import os
import time
from datetime import datetime

LOG_DIR = "logs"  # Adjust if needed
RETENTION_DAYS = 30  # Change this to configure how long logs should be kept

def setup_logger():
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)

    log_filename = os.path.join(log_directory, f"error_logging_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename, mode="w", encoding="utf-8"),
            logging.StreamHandler()
        ],
    )

def purge_old_logs():
    """Deletes logs older than RETENTION_DAYS from the logs directory."""
    now = time.time()
    cutoff = now - (RETENTION_DAYS * 86400)  # Convert days to seconds

    if not os.path.exists(LOG_DIR):
        return  # No logs to purge

    for log_file in os.listdir(LOG_DIR):
        log_path = os.path.join(LOG_DIR, log_file)
        if os.path.isfile(log_path):
            file_mtime = os.path.getmtime(log_path)
            if file_mtime < cutoff:
                os.remove(log_path)
                print(f"🧹 Deleted old log: {log_file}")

# Call this function on startup
purge_old_logs()