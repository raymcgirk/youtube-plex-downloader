import os
import subprocess
import json
import shutil
import logging
import time
import threading
from utils.cache import load_cache, save_cache
from config.loader import load_config
from youtube.downloader import download_video, PLEX_DIRECTORY  # Assuming downloader.py handles downloads
from utils.sanitizer import sanitize_filename

# Load configuration
config = load_config()
CACHE_FILE = config["cache_file"]
CHANNELS = [channel["url"] for channel in config["channels"] if channel["enabled"]]
STAGING_DIRECTORY = config["staging_directory"]

# Load cache with thread safety
cache_lock = threading.Lock()
video_list = load_cache(CACHE_FILE)


import random  # Import random for sleep timing

def process_single_video(video_url, channel, cookies_path):
    """Processes a single video: fetch metadata, download, embed, and move."""

    with cache_lock:
        processed_videos = {video["url"] for video in video_list.get(channel, [])}

    video_entry = None  # ✅ Ensure video_entry is always initialized

    # ✅ Step 1: Check if metadata is already fetched
    if video_url in processed_videos:
        logging.info(f"✅ Metadata already fetched: {video_url}")

        # ✅ Retrieve existing metadata from cache
        with cache_lock:
            for vid in video_list.get(channel, []):
                if vid["url"] == video_url:
                    video_entry = vid
                    break  # ✅ Found the metadata, no need to continue
    else:
        logging.info(f"🛡 Fetching metadata for {video_url}")
        metadata_command = ["yt-dlp", "--cookies", cookies_path, "--dump-json", video_url]

        try:
            with subprocess.Popen(metadata_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                  bufsize=1) as process:
                for line in process.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        video_data = json.loads(line)
                        video_entry = {
                            "title": video_data.get("title", "Unknown"),
                            "uploader": video_data.get("uploader", "UnknownUploader"),
                            "url": video_data.get("webpage_url", video_url),
                            "upload_date": video_data.get("upload_date", "9999-12-31")
                        }
                        break  # ✅ Exit after first valid JSON response
                    except json.JSONDecodeError:
                        continue
                else:
                    logging.error(f"❌ Failed to fetch metadata for {video_url}")
                    return  # Exit function if metadata fetch fails

            with cache_lock:
                video_list.setdefault(channel, []).append(video_entry)
                save_cache(video_list, CACHE_FILE, finalize=True)

        except Exception as e:
            logging.error(f"⚠ Error fetching metadata for {video_url}: {str(e)}")
            return

    # ✅ Step 2: Call yt-dlp to handle downloading decision
    downloaded = download_video(video_url)

    # ✅ Step 3: Handle the result from yt-dlp
    if downloaded is False:
        return  # ✅ Skip to next video immediately (NO sleep timer)

    # ✅ Step 4: Embed metadata after download completes (Ensure video_entry is valid)
    if video_entry:
        logging.info(f"📀 Embedding metadata into {video_entry['title']}")

    sanitized_title = sanitize_filename(video_entry["title"])  # ✅ Use the sanitizer function
    video_path = os.path.join(STAGING_DIRECTORY, f"{video_entry['uploader']}",
                              f"{video_entry['uploader']} - {sanitized_title}.mp4")
    plex_folder = os.path.join(PLEX_DIRECTORY, video_entry["uploader"])
    os.makedirs(plex_folder, exist_ok=True)  # Ensure the folder exists

    final_path = os.path.join(plex_folder, os.path.basename(video_path))

    # ✅ Step 5: Identify and delete the .jpg file after embedding
    thumbnail_path = video_path.replace(".mp4", ".jpg")  # Assume same name as video
    logging.debug(f"DEBUG: Checking for thumbnail file: {thumbnail_path}")

    if os.path.exists(thumbnail_path):
        try:
            os.remove(thumbnail_path)
            logging.info(f"🗑 Deleted embedded thumbnail: {thumbnail_path}")
        except Exception as e:
            logging.error(f"❌ Failed to delete thumbnail: {thumbnail_path} - {e}")
    else:
        logging.debug(f"DEBUG: No thumbnail found to delete: {thumbnail_path}")

    # ✅ Step 6: Move to final Plex storage
    plex_folder = os.path.join(PLEX_DIRECTORY, video_entry["uploader"])
    os.makedirs(plex_folder, exist_ok=True)  # Ensure the folder exists

    logging.debug(f"DEBUG: Checking if file exists at {video_path}")
    if not os.path.exists(video_path):
        logging.error(f"❌ File not found at expected location: {video_path}")
        return  # Exit early if the file is missing

    logging.info(f"📂 Moving file to {final_path}")
    try:
        shutil.move(video_path, final_path)
    except Exception as e:
        logging.error(f"❌ Failed to move file to Plex: {e}")

    # ✅ Step 7: Sleep for a random 30-60 seconds before processing the next video (ONLY IF A VIDEO WAS DOWNLOADED)
    sleep_time = random.randint(30, 60)
    logging.info(f"⏳ Sleeping for {sleep_time} seconds before next video")
    time.sleep(sleep_time)

def get_all_videos():
    """Sequentially processes each video for all enabled channels."""
    for channel in CHANNELS:
        logging.info(f"🛡 Processing videos from {channel}")
        cookies_path = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")

        # Fetch video URLs (ONE AT A TIME)
        yt_dlp_command = ["yt-dlp", "--flat-playlist", "--cookies", cookies_path, "--dump-json", "--playlist-reverse",
                          channel]

        with subprocess.Popen(yt_dlp_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              bufsize=1) as process:
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    video_data = json.loads(line)
                    process_single_video(video_data["url"], channel, cookies_path)
                except json.JSONDecodeError:
                    continue

if __name__ == "__main__":
    get_all_videos()
