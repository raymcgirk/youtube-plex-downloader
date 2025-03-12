import os
import re
import time
import shutil
import subprocess
import json
import random
from datetime import datetime
import logging

log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)  # ✅ Create logs folder if it doesn't exist

log_filename = os.path.join(log_directory, f"error_logging_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")

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

# ✅ Emoji removal function
def remove_emojis(text):
    emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)  # ✅ Match all emojis
    return emoji_pattern.sub("", text)  # ✅ Remove emojis

# Load config file
CONFIG_FILE = "config.json"

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

# Extract paths
STAGING_DIRECTORY = config["staging_directory"]
PLEX_DIRECTORY = config["plex_directory"]
DOWNLOAD_ARCHIVE = config["download_archive"]
CACHE_FILE = config["cache_file"]

# Load only enabled channels
CHANNELS = [channel["url"] for channel in config["channels"] if channel["enabled"]]

logging.info(f"📺 Enabled YouTube Channels: {len(CHANNELS)}")
for channel in CHANNELS:
    logging.info(f" - {channel}")

# Use values from config.json
DOWNLOAD_PATH = os.path.join(STAGING_DIRECTORY, "%(uploader)s", "%(uploader)s - %(title)s.%(ext)s")

# yt-dlp options
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
]

# ✅ Ensure only one log per directory
printed_folders = set()

def update_yt_dlp():
    """Check for and update yt-dlp before running downloads."""
    logging.info("🔄 Checking for yt-dlp updates...")
    subprocess.run(["yt-dlp", "-U"], check=False)  # Non-blocking update check

def sanitize_filename(title):
    """Ensure filename matches yt-dlp's automatic renaming rules."""
    # title = re.sub(r'[<>"\\|*]', '', title).strip()  # ✅ Keep `?`, remove other forbidden characters
    title = title.replace("?", "？")  # ✅ Convert normal `?` to full-width `？`
    # title = title.replace("&", "and")  # ✅ Convert ampersands
    title = title.replace("/", "⧸")  # ✅ Convert forward slashes into special forward slashes (`⧸`)
    title = title.replace('"', '＂')  # ✅ Convert quotation marks into special quotation marks (`＂`)
    title = title.replace(":", "：")  # ✅ Ensure `:` aligns with yt-dlp's behavior
    # title = title.encode("utf-8", "ignore").decode("utf-8")  # ✅ Strip weird characters
    return title.strip()  # ✅ Remove any trailing spaces
            
def load_cache():
    """Load cached video list to avoid unnecessary re-scanning."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save the video list cache, keeping track of the latest download per channel."""
    latest_video_dates = {}

    for channel, videos in cache.items():
        if isinstance(videos, list) and videos:  # Ensure we're handling lists
            latest_video = max(v["upload_date"] for v in videos)
            latest_video_dates[channel + "_latest"] = latest_video  # Store updates separately

    # ✅ Now update the cache outside the loop
    cache.update(latest_video_dates)

    # ✅ Write to file
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

def get_all_videos():
    """Fetch video metadata incrementally (only new videos)."""
    video_list = load_cache()

    for channel in CHANNELS:
        latest_known = video_list.get(channel + "_latest", "20000101")  # Default to old date if none exists
        
        logging.info(f"📡 Fetching new videos from {channel} (only after {latest_known})")

        try:
            result = subprocess.run(
                ["yt-dlp", "--dateafter", latest_known, "--dump-json", channel],
                capture_output=True, text=True, check=True
            )

            new_videos = []
            for line in result.stdout.splitlines():
                try:
                    video_data = json.loads(line)
                    new_videos.append({
                        "title": video_data.get("title"),
                        "uploader": video_data.get("uploader", "UnknownUploader"),
                        "url": video_data.get("webpage_url"),
                        "upload_date": datetime.strptime(video_data.get("upload_date"), "%Y%m%d").isoformat()
                    })
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logging.error(f"⚠️ Skipping malformed video entry: {e}")

            if new_videos:
                if channel not in video_list:
                    video_list[channel] = []  # ✅ Ensure the channel key exists before appending
                
                video_list[channel].extend(new_videos)  # Add new videos to cache
                logging.info(f"✅ Added {len(new_videos)} new videos for {channel}")

        except subprocess.CalledProcessError as e:
            logging.error(f"⚠️ Failed to fetch video list for {channel}: {e}")

    save_cache(video_list)  # ✅ Save updated cache
    return video_list

def has_existing_metadata(video_path, upload_date):
    """Check if the video file already has the correct upload date metadata."""

    # ✅ Ensure the file exists before checking metadata
    if not os.path.exists(video_path):
        logging.warning(f"⚠️ File not found: {video_path}. Skipping metadata check.")
        return False  # ✅ Always return False if the file is missing

    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_entries", "format_tags", video_path],
            capture_output=True, text=True, encoding="utf-8", check=False
        )

        if result.returncode != 0:
            logging.error(f"⚠️ ffprobe failed for {video_path}. Exit code: {result.returncode}")
            return False

        if not result.stdout.strip():
            logging.warning(f"⚠️ ffprobe returned no metadata for {video_path}. Assuming missing metadata.")
            return False

        metadata = json.loads(result.stdout).get("format", {}).get("tags", {})

        expected_date = upload_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        has_metadata = metadata.get("date") == expected_date or metadata.get("originally_available") == expected_date

        logging.info(f"🔍 Metadata check for {video_path}: {has_metadata}")

        return has_metadata

    except Exception as e:
        logging.error(f"⚠️ Unexpected error checking metadata for {video_path}: {e}")
        return False

def apply_upload_dates(video_path, upload_date):
    """Apply the correct upload date timestamp to a single downloaded video."""
    if not os.path.exists(video_path):
        logging.error(f"⚠️ File not found: {video_path}")
        return

    if has_existing_metadata(video_path, upload_date):
        logging.info(f"✅ Metadata already set for {video_path}. Skipping embedding.")
        return  # ✅ Skip processing if metadata is already correct

    try:
        formatted_plex_date = upload_date.strftime("%Y-%m-%dT%H:%M:%SZ")  # ✅ Plex-compatible format

        # ✅ Embed metadata into the video using FFmpeg
        ffmpeg_cmd = [
            "ffmpeg", "-i", video_path,  # Input file
            "-metadata", f"date={formatted_plex_date}",  # ✅ Set "date" metadata
            "-metadata", f"originally_available={formatted_plex_date}",  # ✅ Set Plex's "Originally Available"
            "-codec", "copy",  # ✅ Copy streams (no re-encoding)
            video_path.replace(".mp4", "_temp.mp4")  # Output temp file
        ]

        subprocess.run(ffmpeg_cmd, check=True)

        # ✅ Replace old file with new file
        os.replace(video_path.replace(".mp4", "_temp.mp4"), video_path)
        logging.info(f"✅ Embedded 'Originally Available' metadata in {video_path}")

    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ Failed to embed metadata for {video_path}: {e}")

def download_channel_thumbnail(channel_url, uploader):
    """Downloads the YouTube channel's profile picture using the correct channel name."""

    logging.info(f"🔍 Checking for channel thumbnail for {uploader}...")

    # ✅ Check if the thumbnail already exists in Plex **before** extracting channel name
    plex_folder = os.path.join(PLEX_DIRECTORY, uploader)
    plex_thumbnail_path = os.path.join(plex_folder, "folder.jpg")

    if os.path.exists(plex_thumbnail_path):
        logging.info(f"✅ Thumbnail already exists in Plex: {plex_thumbnail_path}. Skipping download.")
        return  # ✅ Stop execution here

    # ✅ Extract the actual channel name **only if downloading is necessary**
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "%(url)s", channel_url],
            capture_output=True, text=True, check=True
        )
        video_urls = result.stdout.splitlines()
        if not video_urls:
            raise ValueError("No videos found on the channel!")

        latest_video_url = video_urls[0]  # ✅ Take the most recent video

        result = subprocess.run(
            ["yt-dlp", "--print", "%(uploader)s", latest_video_url],
            capture_output=True, text=True, check=True
        )
        channel_name = result.stdout.strip() or uploader  # ✅ Fallback to uploader if empty
        logging.info(f"✅ Extracted channel name: {channel_name}")

    except (subprocess.CalledProcessError, ValueError) as e:
        logging.error(f"⚠️ Failed to extract channel name for {channel_url}: {e}")
        channel_name = uploader  # ✅ Fallback to URL name if needed

    # ✅ Use extracted channel name for folder paths
    staging_folder = os.path.join(STAGING_DIRECTORY, channel_name)
    plex_folder = os.path.join(PLEX_DIRECTORY, channel_name)

    os.makedirs(staging_folder, exist_ok=True)  # Ensure staging folder exists
    os.makedirs(plex_folder, exist_ok=True)  # Ensure Plex folder exists

    logging.info(f"🔍 Downloading channel thumbnail for {channel_name}...")

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

        logging.info(f"✅ Downloaded thumbnail to staging: {staging_thumbnail_path}")

        # ✅ Move thumbnail to Plex directory
        shutil.move(staging_thumbnail_path, plex_thumbnail_path)
        logging.info(f"✅ Moved thumbnail to Plex: {plex_thumbnail_path}")

    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ yt-dlp failed for {channel_name}: {e}")
    except FileNotFoundError:
        logging.error(f"⚠️ Thumbnail file not found in staging: {staging_thumbnail_path}")
    except Exception as e:
        logging.error(f"⚠️ Unexpected error: {e}")

def download_oldest_videos():
    """Ensure metadata is fetched, then download videos in chronological order."""
    update_yt_dlp()  # ✅ Ensure yt-dlp is up to date before downloading

    videos = load_cache()

    # ✅ Check if any new channels are missing from the cache and update
    missing_channels = [channel for channel in CHANNELS if channel not in videos]
    if missing_channels:
        logging.info(f"🔄 Fetching video metadata for new channels: {missing_channels}")
        videos = get_all_videos()  # ✅ Force an update to the cache

    if not videos:
        logging.info("⚠️ Still no videos found after fetching. Exiting.")
        return
        
    # ✅ Now we download thumbnails—after confirming video metadata.
    for channel in CHANNELS:
        uploader = channel.split("/")[-1].lstrip("@")  # Remove '@' if present
        download_channel_thumbnail(channel, uploader)

    # ✅ Ensure videos are sorted by upload_date
    sorted_videos = []
    for channel, video_list in videos.items():
        if "_latest" in channel:  # ✅ Skip _latest tracking keys
            continue
        if isinstance(video_list, list):  # ✅ Ensure it's a list
            sorted_videos.extend(video_list)
        else:
            logging.error(f"⚠️ Invalid data format for channel {channel}: Expected a list, got {type(video_list)}")

    # ✅ Ensure all items in sorted_videos are dictionaries
    sorted_videos = [v for v in sorted_videos if isinstance(v, dict)]

    # ✅ Check if upload_date exists before sorting
    sorted_videos.sort(key=lambda v: v.get("upload_date", "9999-12-31T23:59:59"))  # Default to far-future date if missing

    for video in sorted_videos:
        sanitized_title = sanitize_filename(video["title"])
        uploader_folder = os.path.join(STAGING_DIRECTORY, video.get("uploader", "UnknownUploader"))
        video_path = os.path.join(uploader_folder, f"{video.get('uploader', 'UnknownUploader')} - {sanitized_title}.mp4")

        # ✅ Print the folder contents ONCE per session
        if uploader_folder not in printed_folders and os.path.exists(uploader_folder):
            logging.info(f"\n📂 Files in {uploader_folder}:")
            for filename in os.listdir(uploader_folder):
                logging.info(f" - {filename}")
            printed_folders.add(uploader_folder)

        # ✅ Check if the file already exists in STAGING
        if os.path.exists(video_path):
            logging.info(f"✅ File already exists: {video_path}")

            try:
                upload_date = datetime.strptime(video["upload_date"], "%Y-%m-%dT%H:%M:%S")

                # ✅ Check if metadata is missing
                if not has_existing_metadata(video_path, upload_date):
                    logging.info(f"🛠 Metadata missing. Embedding metadata for: {video_path}")
                    apply_upload_dates(video_path, upload_date)
                else:
                    logging.info(f"✅ Metadata already embedded. Skipping metadata processing.")
                           
            except ValueError as e:
                logging.error(f"⚠️ Error parsing upload date for {video['title']}: {e}")
                continue  # ✅ Skip to the next video if metadata is invalid

        else:
            # ✅ Check both staging and Plex directories first
            final_video_path = os.path.join(PLEX_DIRECTORY, video.get("uploader", "UnknownUploader"),
                                            f"{video.get('uploader', 'UnknownUploader')} - {sanitized_title}.mp4")
            video_path = os.path.join(STAGING_DIRECTORY, video.get("uploader", "UnknownUploader"),
                                      f"{video.get('uploader', 'UnknownUploader')} - {sanitized_title}.mp4")

            file_in_staging = os.path.exists(video_path)
            file_in_plex = os.path.exists(final_video_path)

            # ✅ Skip download if the file already exists in either location
            if file_in_staging or file_in_plex:
                logging.info(f"✅ File already exists, skipping download: {final_video_path if file_in_plex else video_path}")
                continue  # ✅ Skip this video

            # ✅ If file does NOT exist, THEN log "Downloading..."
            logging.info(f"📥 Downloading to STAGING: {video['title']} ({video['upload_date']})")
            
            # ✅ Define the yt-dlp command before calling subprocess
            command = YTDLP_OPTIONS + [video["url"]]
            
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            already_in_archive = False  # ✅ Track if yt-dlp reports archive message

            for line in process.stdout:
                line = line.strip()
                if not line or any(skip in line for skip in ["[download]", "[ffmpeg]"]):
                    continue  # ✅ Ignore empty lines and irrelevant yt-dlp output
                if "has already been recorded in the archive" in line:
                    already_in_archive = True
                if "Downloading" in line or "Merging formats into" in line:
                    logging.info(line)  # ✅ Only log important messages

            process.wait()

            if process.returncode != 0:
                logging.error(f"⚠️ Download failed for {video['title']} with exit code {process.returncode}")
                continue  # ✅ Skip to the next video if yt-dlp fails

            logging.info(f"🛠 Checking if file exists at: {video_path}")

            # ✅ Check both staging and final destination before assuming it's missing
            final_video_path = os.path.join(PLEX_DIRECTORY, video.get("uploader", "UnknownUploader"),
                                            f"{video.get('uploader', 'UnknownUploader')} - {sanitized_title}.mp4")

            # ✅ Check if the file exists in either staging or Plex
            file_in_staging = os.path.exists(video_path)
            file_in_plex = os.path.exists(final_video_path)

            # ✅ Check if the file exists in either Staging or Plex, and only log necessary messages
            if file_in_plex:
                logging.info(f"🔍 File already exists in PLEX: {final_video_path}")
                continue  # ✅ No need to check further if it's already in Plex

            if not file_in_staging:
                logging.error(f"⚠️ Expected file missing: {video_path} - Not found in staging or Plex.")
                continue  # ✅ Skip to next video if truly missing

            # ✅ Embed metadata after downloading
            try:
                upload_date = datetime.strptime(video["upload_date"], "%Y-%m-%dT%H:%M:%S")
                apply_upload_dates(video_path, upload_date)
            except ValueError as e:
                logging.error(f"⚠️ Error parsing upload date for {video['title']}: {e}")
                continue  # ✅ Skip if the upload date is invalid

        # ✅ Move file to Plex **AFTER metadata is processed**
        final_uploader_folder = os.path.join(PLEX_DIRECTORY, video.get("uploader", "UnknownUploader"))
        final_video_path = os.path.join(final_uploader_folder, f"{video.get('uploader', 'UnknownUploader')} - {sanitized_title}.mp4")

        # ✅ If the file is already in Plex, log it and skip moving
        if os.path.exists(final_video_path):
            logging.info(f"🔍 File already exists in PLEX: {final_video_path}")
            continue  # ✅ Skip moving this file

        if not os.path.exists(final_uploader_folder):
            os.makedirs(final_uploader_folder)  # ✅ Create folder if needed

        try:
            # ✅ Move all associated files (mp4, jpg, etc.)
            for file in os.listdir(uploader_folder):
                if file.startswith(f"{video.get('uploader', 'UnknownUploader')} - {sanitized_title}"):
                    file_path = os.path.join(uploader_folder, file)
                    destination_path = os.path.join(final_uploader_folder, file)
                    shutil.move(file_path, destination_path)
                    logging.info(f"✅ Moved {file} to PLEX: {destination_path}")
        except Exception as e:
            logging.error(f"⚠️ Failed to move {video_path} to PLEX directory: {e}")
            continue  # ✅ Skip if move fails

        # ✅ Skip sleep if yt-dlp reported "already in archive"
        if already_in_archive:
            logging.info("⏭️ Skipping sleep since video was already recorded in the archive.")
            continue
        
        # ✅ Add a manual sleep after downloads (if needed)
        sleep_time = random.randint(30, 60)
        logging.info(f"⏳ Sleeping for {sleep_time} seconds before the next download...")
        time.sleep(sleep_time)  
            
if __name__ == "__main__":
    download_oldest_videos()
    
