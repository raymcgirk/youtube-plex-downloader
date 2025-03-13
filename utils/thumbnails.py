import os
import logging
import subprocess
import shutil
from config.loader import load_config

config = load_config()

STAGING_DIRECTORY = config["staging_directory"]
PLEX_DIRECTORY = config["plex_directory"]

def download_channel_thumbnail(channel_url: str, uploader: str):
    logging.info(f"🔍 Checking channel thumbnail for {uploader}...")

    uploader = str(uploader)

    plex_folder = os.path.join(str(PLEX_DIRECTORY), uploader)
    plex_thumbnail_path = os.path.join(plex_folder, "folder.jpg")

    if os.path.exists(plex_thumbnail_path):
        logging.info(f"✅ Thumbnail already exists: {plex_thumbnail_path}")
        return

    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "%(url)s", channel_url],
            capture_output=True, text=True, check=True
        )
        video_urls = result.stdout.splitlines()
        if not video_urls:
            raise ValueError("No videos found on the channel.")

        latest_video_url = video_urls[0]

        result = subprocess.run(
            ["yt-dlp", "--print", "%(uploader)s", latest_video_url],
            capture_output=True, text=True, check=True
        )
        channel_name = result.stdout.strip() or uploader
        logging.info(f"✅ Extracted channel name: {channel_name}")

    except (subprocess.CalledProcessError, ValueError) as e:
        logging.error(f"⚠️ Error extracting channel name: {e}")
        channel_name = uploader

    channel_name = str(channel_name)

    staging_folder = os.path.join(str(STAGING_DIRECTORY), channel_name)
    plex_folder = os.path.join(PLEX_DIRECTORY, channel_name)

    os.makedirs(staging_folder, exist_ok=True)
    os.makedirs(plex_folder, exist_ok=True)

    staging_thumbnail_path = os.path.join(staging_folder, "folder.jpg")

    try:
        subprocess.run([
            "yt-dlp",
            "--write-thumbnail",
            "--skip-download",
            "--convert-thumbnails", "jpg",
            "--playlist-items", "0",
            "-o", os.path.join(staging_folder, "folder"),
            channel_url
        ], check=True)

        shutil.move(staging_thumbnail_path, plex_thumbnail_path)
        logging.info(f"✅ Thumbnail moved to Plex: {plex_thumbnail_path}")

    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ yt-dlp failed: {e}")
    except FileNotFoundError:
        logging.error(f"⚠️ Thumbnail not found in staging: {staging_thumbnail_path}")
    except Exception as e:
        logging.error(f"⚠️ Unexpected error: {e}")