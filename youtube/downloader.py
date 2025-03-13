import subprocess
import os
import random
import time
import logging
import shutil
from datetime import datetime

from utils.sanitizer import sanitize_filename
from plex.embedder import apply_upload_dates, has_existing_metadata
from utils.cache import load_cache
from config.loader import load_config
from youtube.utils import update_yt_dlp
from youtube.fetcher import get_all_videos
from utils.thumbnails import download_channel_thumbnail

config = load_config()

STAGING_DIRECTORY = config["staging_directory"]
PLEX_DIRECTORY = config["plex_directory"]
DOWNLOAD_ARCHIVE = config["download_archive"]
CACHE_FILE = config["cache_file"]
CHANNELS = [channel["url"] for channel in config["channels"] if channel["enabled"]]

DOWNLOAD_PATH = os.path.join(STAGING_DIRECTORY, "%(uploader)s", "%(uploader)s - %(title)s.%(ext)s")

YTDLP_OPTIONS = [
    "yt-dlp",
    "-f", "bv*[height<=1080]+ba/b[height<=1080]",
    "-o", DOWNLOAD_PATH,
    "--merge-output-format", "mp4",
    "--remux-video", "mp4",
    "--no-part",
    "--force-overwrites",
    "--write-thumbnail",
    "--convert-thumbnails", "jpg",
    "--embed-metadata",
    "--embed-thumbnail",
    "--limit-rate", "2M",
    "--retries", "10",
    "--download-archive", DOWNLOAD_ARCHIVE,
    "--sponsorblock-remove", "sponsor,selfpromo,intro,outro",
    "--print-traffic",
    "--match-filter", "!is_live & availability!=needs_auth & !is_short"
]

printed_folders = set()

def download_oldest_videos():
    update_yt_dlp()

    videos = load_cache(CACHE_FILE)

    missing_channels = [channel for channel in CHANNELS if channel not in videos]
    if missing_channels:
        logging.info(f"🔄 Fetching video metadata for new channels: {missing_channels}")
        videos = get_all_videos()

    if not videos:
        logging.info("⚠️ Still no videos found after fetching. Exiting.")
        return

    for channel in CHANNELS:
        uploader = channel.split("/")[-1].lstrip("@")
        download_channel_thumbnail(channel, uploader)

    sorted_videos = []
    for channel, video_list in videos.items():
        if "_latest" in channel:
            continue
        if isinstance(video_list, list):
            sorted_videos.extend(video_list)
        else:
            logging.error(f"⚠️ Invalid data format for channel {channel}: {type(video_list)}")

    sorted_videos = [v for v in sorted_videos if isinstance(v, dict)]
    sorted_videos.sort(key=lambda v: v.get("upload_date", "9999-12-31T23:59:59"))

    for video in sorted_videos:
        sanitized_title = sanitize_filename(video["title"])
        uploader = video.get("uploader", "UnknownUploader")

        uploader_folder = os.path.join(STAGING_DIRECTORY, uploader)
        video_path = os.path.join(uploader_folder, f"{uploader} - {sanitized_title}.mp4")

        if uploader_folder not in printed_folders and os.path.exists(uploader_folder):
            logging.info(f"\n📂 Files in {uploader_folder}:")
            for filename in os.listdir(uploader_folder):
                logging.info(f" - {filename}")
            printed_folders.add(uploader_folder)

        if os.path.exists(video_path):
            logging.info(f"✅ File already exists: {video_path}")

            try:
                upload_date = datetime.strptime(video["upload_date"], "%Y-%m-%dT%H:%M:%S")

                if not has_existing_metadata(video_path, upload_date):
                    logging.info(f"🛠 Metadata missing. Embedding metadata for: {video_path}")
                    apply_upload_dates(video_path, upload_date)
                else:
                    logging.info("✅ Metadata already embedded. Skipping.")

            except ValueError as e:
                logging.error(f"⚠️ Error parsing upload date for {video['title']}: {e}")
                continue

        else:
            final_video_path = os.path.join(PLEX_DIRECTORY, uploader, f"{uploader} - {sanitized_title}.mp4")
            video_path = os.path.join(STAGING_DIRECTORY, uploader, f"{uploader} - {sanitized_title}.mp4")

            file_in_staging = os.path.exists(video_path)
            file_in_plex = os.path.exists(final_video_path)

            if file_in_staging or file_in_plex:
                logging.info(f"✅ Already exists, skipping download: {final_video_path if file_in_plex else video_path}")
                continue

            logging.info(f"📥 Downloading to STAGING: {video['title']} ({video['upload_date']})")

            command = YTDLP_OPTIONS + [video["url"]]

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            already_in_archive = False

            for line in process.stdout:
                line = line.strip()
                if not line or any(skip in line for skip in ["[download]", "[ffmpeg]"]):
                    continue
                if "has already been recorded in the archive" in line:
                    already_in_archive = True
                if "Downloading" in line or "Merging formats into" in line:
                    logging.info(line)

            process.wait()

            if process.returncode != 0:
                logging.error(f"⚠️ Download failed for {video['title']} (exit code {process.returncode})")
                continue

            if not os.path.exists(video_path):
                logging.error(f"⚠️ Expected file missing: {video_path}")
                continue

            try:
                upload_date = datetime.strptime(video["upload_date"], "%Y-%m-%dT%H:%M:%S")
                apply_upload_dates(video_path, upload_date)
            except ValueError as e:
                logging.error(f"⚠️ Error parsing upload date: {e}")
                continue

            final_uploader_folder = os.path.join(PLEX_DIRECTORY, uploader)

            if not os.path.exists(final_uploader_folder):
                os.makedirs(final_uploader_folder)

            try:
                for file in os.listdir(uploader_folder):
                    if file.startswith(f"{uploader} - {sanitized_title}"):
                        source_path = os.path.join(uploader_folder, file)
                        destination_path = os.path.join(final_uploader_folder, file)
                        shutil.move(source_path, destination_path)
                        logging.info(f"✅ Moved {file} to Plex: {destination_path}")
            except Exception as e:
                logging.error(f"⚠️ Move failed: {e}")
                continue

            if already_in_archive:
                logging.info("⏭️ Skipping sleep since video was already recorded in the archive.")
                continue

            sleep_time = random.randint(30, 60)
            logging.info(f"⏳ Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
