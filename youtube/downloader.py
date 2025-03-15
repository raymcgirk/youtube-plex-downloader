import os
import re
import time
import logging
import subprocess
from tqdm import tqdm
from config.loader import load_config
from logger.logger import get_yt_dlp_log_path, cleanup_old_logs

config = load_config()

STAGING_DIRECTORY = config["staging_directory"]
PLEX_DIRECTORY = config["plex_directory"]
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # Get root project directory
MAIN_DIRECTORY = os.path.dirname(PROJECT_ROOT)
DOWNLOAD_ARCHIVE = os.path.join(MAIN_DIRECTORY, "downloaded.txt")
CACHE_FILE = config["cache_file"]

DOWNLOAD_PATH = os.path.join(STAGING_DIRECTORY, "%(uploader)s", "%(uploader)s - %(title)s.%(ext)s")

YTDLP_OPTIONS = [
    "yt-dlp",
    "-f", "bv*[height<=1080]+ba/b[height<=1080]",
    "-o", DOWNLOAD_PATH,
    "--merge-output-format", "mp4",
    "--remux-video", "mp4",
    "--force-overwrites",
    "--write-thumbnail",
    "--convert-thumbnails", "jpg",
    "--embed-metadata",
    "--embed-thumbnail",
    "--rm-cache-dir",
    "--limit-rate", "5M",
    "--retries", "10",
    "--download-archive", DOWNLOAD_ARCHIVE,
    "--sponsorblock-remove", "sponsor,selfpromo,intro,outro",
    "--print-traffic",
    "--match-filter", "!is_live & availability!=needs_auth & !is_short"
]


def is_video_downloaded(video_url):
    """Checks if the video is already recorded in yt-dlp's download archive by matching only the video ID."""
    if not os.path.exists(DOWNLOAD_ARCHIVE):
        logging.info(f"⚠ Archive file not found: {DOWNLOAD_ARCHIVE}")
        return False  # Archive file doesn't exist yet

    video_id = video_url.split("v=")[-1]  # ✅ Extract only the video ID from full URL

    logging.debug(f"DEBUG: Checking if video ID '{video_id}' is in {DOWNLOAD_ARCHIVE}")

    with open(DOWNLOAD_ARCHIVE, "r") as archive_file:
        for line in archive_file:
            if video_id.strip() in line.strip():  # ✅ Now we correctly check for the video ID
                logging.info(f"✅ Already downloaded: {video_url}, skipping.")
                return True  # ✅ Video was already downloaded

    logging.debug(f"DEBUG: Video ID '{video_id}' NOT found in archive!")
    return False  # ❌ Not found in archive

def download_video(video_url):
    """Downloads a specific video using yt-dlp and returns True if downloaded, False if skipped"""

    # ✅ Step 1: Check if the video is in the archive BEFORE calling yt-dlp
    if is_video_downloaded(video_url):
        return False  # ✅ Skip the video immediately

    command = YTDLP_OPTIONS + [video_url]
    yt_dlp_log_filename = get_yt_dlp_log_path()
    download_started = False

    log_directory = os.path.dirname(yt_dlp_log_filename)
    os.makedirs(log_directory, exist_ok=True)  # ✅ Ensure logs directory exists
    open(yt_dlp_log_filename, "w").close()  # ✅ Create an empty log file

    try:
        logging.debug(f"Running yt-dlp with command: {' '.join(command)}")

        # ✅ Redirect yt-dlp output directly to the log file
        with open(yt_dlp_log_filename, "w", encoding="utf-8") as log_file:
            process = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT, text=True)

        # ✅ Initialize progress bar ONLY IF downloading starts
        progress_bar = None

        while process.poll() is None:
            time.sleep(1)

            if not os.path.exists(yt_dlp_log_filename):
                continue  # ✅ Retry if the log file hasn't been created yet

            with open(yt_dlp_log_filename, "r") as log_reader:
                log_content = log_reader.readlines()

            for line in reversed(log_content):
                line = line.strip()

                # ✅ Detect when yt-dlp actually starts downloading
                if "[download]" in line and "Destination" in line and not download_started:
                    logging.info(f"📥 Downloading: {video_url}")
                    download_started = True

                # ✅ Ensure progress bar only starts if downloading begins
                if download_started and not progress_bar:
                    progress_bar = tqdm(total=100, desc="Downloading", unit="%", dynamic_ncols=True, leave=True)

                # ✅ Extract progress percentage
                match = re.search(r"(\d{1,3}\.\d+)%", line)
                if match and progress_bar:
                    percent_complete = float(match.group(1))
                    progress_bar.n = int(percent_complete)
                    progress_bar.refresh()
                    break

        process.wait()
        if progress_bar:
            progress_bar.close()

        cleanup_old_logs()

        return process.returncode == 0  # ✅ True if download succeeded, False otherwise

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Failed to download {video_url}: {e}")
        return None  # ❌ Return None if yt-dlp encountered an unexpected error