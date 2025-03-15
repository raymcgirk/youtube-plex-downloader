import logging
import os
from datetime import datetime, timedelta

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

def get_yt_dlp_log_path():
    """Returns the file path for yt-dlp logging."""
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)
    return os.path.join(log_directory, f"yt-dlp-debug_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

def cleanup_old_logs(log_directory="logs", prefix="yt-dlp-debug_", days=30):
    """Deletes yt-dlp logs older than 30 days."""
    cutoff_date = datetime.now() - timedelta(days=days)

    for filename in os.listdir(log_directory):
        if filename.startswith(prefix):
            log_path = os.path.join(log_directory, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(log_path))

            if file_time < cutoff_date:
                os.remove(log_path)
                logging.info(f"🗑 Deleted old log: {log_path}")