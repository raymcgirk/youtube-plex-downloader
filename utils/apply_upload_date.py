import os
import json
import subprocess
from datetime import datetime
import logging

# Load configuration from config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
    config = json.load(config_file)

CACHE_FILE = config["cache_file"]
BASE_DIRECTORY = config["plex_directory"]

# ✅ Ensure the "logs" directory exists
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)  # ✅ Create the folder if it doesn't exist

# ✅ Generate a unique log filename with timestamp inside "logs/"
log_filename = os.path.join(log_directory, f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# ✅ Configure logging to save logs inside "logs/" folder
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_filename, mode="w", encoding="utf-8", errors="ignore"),  # ✅ Save logs inside "logs/" folder
        logging.StreamHandler()  # ✅ Also print logs to console
    ],
)

def load_cache():
    """Load video metadata from video_cache.json."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sanitize_filename(title):
    """Ensure filename matches yt-dlp's automatic renaming rules."""
    title = title.replace("?", "？")
    title = title.replace("/", "⧸")
    title = title.replace('"', '＂')
    title = title.replace(":", "：")
    title = title.replace("|", "｜")
    return title.strip()


def embed_metadata(video_path, upload_date):
    """Embed the correct upload date metadata inside the MP4 file using FFmpeg."""
    formatted_plex_date = upload_date.strftime("%Y-%m-%dT%H:%M:%SZ")  # ✅ Plex-compatible format
    logging.info(f"🕒 Using upload date: {formatted_plex_date} for {video_path}")

    # ✅ FFmpeg command to embed metadata
    ffmpeg_cmd = [
        "ffmpeg", "-i", video_path,  # Input file
        "-metadata", f"date={formatted_plex_date}",  # ✅ Set "date" metadata
        "-metadata", f"metadata_creation_time={formatted_plex_date}", # ✅ Set Plex's "Originally Available"
        "-codec", "copy",  # ✅ Copy streams (no re-encoding)
        video_path.replace(".mp4", "_temp.mp4")  # Output temp file
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)

        # ✅ Replace old file with new file
        os.replace(video_path.replace(".mp4", "_temp.mp4"), video_path)
        logging.info(f"✅ Embedded 'Originally Available' metadata in {video_path}")

    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ Failed to embed metadata for {video_path}: {e}")

def apply_upload_dates():
    """Loop through downloaded videos and apply the correct upload date."""
    cache = load_cache()

    if not cache:
        logging.info("⚠️ No data found in video_cache.json!")
        return

    printed_folders = set()  # ✅ Define the set before using it

    for channel, videos in cache.items():
        for video in videos:
            video_title = sanitize_filename(video["title"])  # ✅ Apply sanitization
            upload_date_str = video["upload_date"]
            uploader_folder = os.path.join(BASE_DIRECTORY, video["uploader"])

            # ✅ Only print the directory contents ONCE
            if uploader_folder not in printed_folders and os.path.exists(uploader_folder):
                logging.info(f"\n📂 Files in {uploader_folder}:")
                for filename in os.listdir(uploader_folder):
                    logging.info(f" - {filename}")
                printed_folders.add(uploader_folder)  # ✅ Mark this folder as printed

            # ✅ Define `video_file` before using it
            video_file = os.path.join(uploader_folder, f"{video['uploader']} - {video_title}.mp4")

            # ✅ Print expected vs actual filenames
            logging.info(f"🔍 Looking for: {video_file}")

            if not os.path.exists(video_file):
                logging.error(f"⚠️ File not found: {video_file}")
                continue

            try:
                upload_date = datetime.strptime(upload_date_str, "%Y%m%d")
                embed_metadata(video_file, upload_date)  # ✅ Now embeds metadata
            except ValueError as e:
                logging.error(f"⚠️ Error parsing upload date for {video_title}: {e}")

if __name__ == "__main__":
    apply_upload_dates()