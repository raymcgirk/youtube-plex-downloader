import os
import subprocess
import json
import logging
import threading
from utils.cache import load_cache, save_cache
from config.loader import load_config

# Load configuration
config = load_config()
CACHE_FILE = config["cache_file"]
CHANNELS = [channel["url"] for channel in config["channels"] if channel["enabled"]]

# Load cache (progress tracking) with thread safety
cache_lock = threading.Lock()
video_list = load_cache(CACHE_FILE)

def get_all_videos():
    for channel in CHANNELS:
        logging.info(f"🛡 Fetching ALL metadata from {channel} (Resume Supported)")
        cookies_path = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")

        # Load existing progress safely inside lock
        with cache_lock:
            processed_videos = set(video["url"] for video in video_list.get(channel, []))
            video_list.setdefault(channel, [])

        # ✅ Step 1: Fetch all video URLs
        yt_dlp_command = [
            "yt-dlp",
            "--flat-playlist",
            "--cookies", cookies_path,
            "--dump-json", channel
        ]

        logging.info(f"🚀 Running yt-dlp command: {' '.join(yt_dlp_command)}")
        video_urls = []

        # Use `with subprocess.Popen()` to prevent resource leaks
        with subprocess.Popen(
            yt_dlp_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        ) as process:
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    video_data = json.loads(line)
                    video_url = video_data["url"]
                    if video_url not in processed_videos:  # ✅ Only process new videos
                        video_urls.append(video_url)
                except json.JSONDecodeError:
                    continue

            process.wait()

        # ✅ Step 2: Fetch full metadata for new videos
        for video_url in video_urls:
            logging.info(f"🛡 Fetching full metadata for {video_url}")
            metadata_command = [
                "yt-dlp",
                "--cookies", cookies_path,
                "--dump-json", video_url
            ]

            with subprocess.Popen(
                metadata_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
            ) as process:
                for line in process.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        video_data = json.loads(line)
                        upload_date = video_data.get("upload_date", "9999-12-31")

                        # ✅ LOG Video Metadata
                        logging.info(f"🎥 Processing: {video_data.get('title', 'Unknown')} | {upload_date}")

                        video_entry = {
                            "title": video_data.get("title", "Unknown"),
                            "uploader": video_data.get("uploader", "UnknownUploader"),
                            "url": video_data.get("webpage_url", "Unknown URL"),
                            "upload_date": upload_date
                        }

                        with cache_lock:
                            video_list[channel].append(video_entry)
                            processed_videos.add(video_url)  # ✅ Mark as processed
                            save_cache(video_list, CACHE_FILE, finalize=False)  # Save incrementally
                    except json.JSONDecodeError:
                        pass

                process.wait()

if __name__ == "__main__":
    get_all_videos()
