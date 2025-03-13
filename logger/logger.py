import logging
import os
from datetime import datetime

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
