import os
import json
from datetime import datetime
import subprocess
import logging


def apply_upload_dates(video_path, upload_date):
    """Apply the correct upload date timestamp to a single downloaded video."""
    if not os.path.exists(video_path):
        logging.error(f"⚠️ File not found: {video_path}")
        return

    formatted_plex_date = upload_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    temp_video_path = video_path.replace(".mp4", "_temp.mp4")

    # Embed metadata using FFmpeg (added metadata_creation_time for Plex compatibility)
    try:
        subprocess.run([
            "ffmpeg", "-i", video_path,
            "-metadata", f"date={formatted_plex_date}",
            "-metadata", f"originally_available={formatted_plex_date}",
            "-metadata", f"metadata_creation_time={formatted_plex_date}",  # ✅ Plex's "Originally Available"
            "-codec", "copy",
            temp_video_path
        ], check=True)

        os.replace(temp_video_path, video_path)
        logging.info(f"✅ Embedded metadata into {video_path}")

    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ Failed to embed metadata for {video_path}: {e}")
    except Exception as e:
        logging.error(f"⚠️ Unexpected error embedding metadata for {video_path}: {e}")


def process_videos(cache_data):
    """Loops through downloaded videos and applies correct upload dates."""
    for channel, videos in cache_data.items():
        for video in videos:
            video_title = video["title"].replace("?", "？").replace("/", "⧸").replace(":", "：")
            upload_date_str = video["upload_date"]
            uploader_folder = os.path.join("/mnt/data/plex_directory", video["uploader"])
            video_file = os.path.join(uploader_folder, f"{video['uploader']} - {video_title}.mp4")

            # ✅ Log folder contents for debugging
            if os.path.exists(uploader_folder):
                logging.info(f"\n📂 Files in {uploader_folder}:")
                for filename in os.listdir(uploader_folder):
                    logging.info(f" - {filename}")

            logging.info(f"🔍 Looking for: {video_file}")
            if not os.path.exists(video_file):
                logging.error(f"⚠️ File not found: {video_file}")
                continue

            try:
                upload_date = datetime.strptime(upload_date_str, "%Y%m%d")
                apply_upload_dates(video_file, upload_date)
            except ValueError as e:
                logging.error(f"⚠️ Error parsing upload date for {video_title}: {e}")


if __name__ == "__main__":
    CACHE_FILE = "/mnt/data/video_cache.json"
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            video_cache = json.load(f)
        process_videos(video_cache)
    else:
        logging.error("⚠️ video_cache.json not found! Cannot process videos.")