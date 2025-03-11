import os
import re
import time
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

# List of YouTube channels or playlists to download
CHANNELS = [
    # "https://www.youtube.com/@AETV",
    "https://www.youtube.com/@BobbyBroccoli",
    # "https://www.youtube.com/@CallMeKevin",
    # "https://www.youtube.com/@CarbotAnimations",
    # "https://www.youtube.com/@CartNarcs",
    "https://www.youtube.com/@ChatHistory",
    "https://www.youtube.com/@ClimateTown",
    # "https://www.youtube.com/@ComedyCentral",
    # "https://www.youtube.com/@CopsTV",
    "https://www.youtube.com/@DougDoug",
    "https://www.youtube.com/@dougdougdoug",
    # "https://www.youtube.com/@dougdougdougdoug",
    # "https://www.youtube.com/@ExploreWithUs",
    "https://www.youtube.com/@FormerlyBlue",
    # "https://www.youtube.com/@FreeDocumentary",
    # "https://www.youtube.com/@FreeDocumentaryNature",
    # "https://www.youtube.com/@Funhaus",
    # "https://www.youtube.com/@GameTheory",
    # "https://www.youtube.com/@HistoryMatters",
    "https://www.youtube.com/@HorrorStories666",
    "https://www.youtube.com/@IronPineapple",
    "https://www.youtube.com/@JCS",
    "https://www.youtube.com/@JaboodyDubs",
    # "https://www.youtube.com/@LawAndCrime",
    # "https://www.youtube.com/@LetsGameItOut",
    "https://www.youtube.com/@LilAggy",
    # "https://www.youtube.com/@MrBallen",
    # "https://www.youtube.com/@MrBallensMedicalfanedit",
    # "https://www.youtube.com/@mrnightmare",
    "https://www.youtube.com/@NanoBaiter",
    # "https://www.youtube.com/@NinjaWarrior",
    "https://www.youtube.com/@NotJustBikes",
    "https://www.youtube.com/@OverSimplified",
    # "https://www.youtube.com/@RealCivilEngineerGaming",
    # "https://www.youtube.com/@RealLifeLore",
    "https://www.youtube.com/@SamONellaAcademy",
    # "https://www.youtube.com/@SethsBikeHacks",
    "https://www.youtube.com/@Shifter_Cycling",
    # "https://www.youtube.com/@SparkDocs",
    "https://www.youtube.com/@Streetcraft",
    "https://www.youtube.com/@TheLaughingSimon",
    # "https://www.youtube.com/@ToastedShoes",
    # "https://www.youtube.com/@VivaLaDirtLeague",
    "https://www.youtube.com/@WartimeStories",
    # "https://www.youtube.com/@astrumspace",
    # "https://www.youtube.com/@distortion2",
    "https://www.youtube.com/@eli_handle_bwav",
    # "https://www.youtube.com/@gcn",
    # "https://www.youtube.com/@jayveeeee",
    "https://www.youtube.com/@kurzgesagt",
    # "https://www.youtube.com/@lockpickinglawyer",
    # "https://www.youtube.com/@mytruecrimenews",
    "https://www.youtube.com/@oddheader",
    "https://www.youtube.com/@reigarw",
    # "https://www.youtube.com/@sciencechannel",
    "https://www.youtube.com/@streetscaping",
    "https://www.youtube.com/@timthelawnmowerman",
    "https://www.youtube.com/@tosh",
    "https://www.youtube.com/@toshshow"
]

# Define file paths
DOWNLOAD_PATH = r"\\mcgirk-server\video\YouTube\%(uploader)s\%(uploader)s - %(title)s.%(ext)s"
DOWNLOAD_ARCHIVE = r"\\mcgirk-server\video\youtube\downloaded.txt"
CACHE_FILE = r"\\mcgirk-server\video\youtube\video_cache.json"
BASE_DIRECTORY = r"\\mcgirk-server\video\YouTube"

# yt-dlp options
YTDLP_OPTIONS = [
    "yt-dlp",
    "-f", "bv*[height<=1080]+ba/b[height<=1080]",
    "-o", DOWNLOAD_PATH,
    "--merge-output-format", "mp4",
    "--remux-video", "mp4",
    "--no-part",
    "--write-thumbnail",
    "--convert-thumbnails", "jpg",
    "--embed-metadata",
    "--embed-thumbnail",
    "--limit-rate", "2M",
    "--retries", "10",
    "--download-archive", DOWNLOAD_ARCHIVE,
    "--sponsorblock-remove", "sponsor,selfpromo,intro,outro"
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
    # title = title.replace("⧸", "")  # ✅ Remove special forward slashes (`⧸`)
    title = title.replace(":", "：")  # ✅ Ensure `:` aligns with yt-dlp's behavior
    # title = title.encode("utf-8", "ignore").decode("utf-8")  # ✅ Strip weird characters
    return title.strip()  # ✅ Remove any trailing spaces
            
# def force_correct_timestamps(file_path, upload_date):
    # """Set 'Date Modified' and 'Date Created' to the correct upload date."""
    # if os.name == "nt":
        # formatted_windows_date = upload_date.strftime("%m/%d/%Y %H:%M:%S")
        # logging.info(f"🔄 Setting timestamps for: {file_path} → {formatted_windows_date}")

        # powershell_cmd = [
            # "powershell", "-Command",
            # f"$file = Get-Item \"{file_path}\"; "
            # f"$file.LastWriteTime = \"{formatted_windows_date}\"; "
            # f"$file.CreationTime = \"{formatted_windows_date}\"; "
            # f"$file.LastAccessTime = \"{formatted_windows_date}\""
        # ]

        # try:
            # subprocess.run(powershell_cmd, check=True)
            # logging.info(f"✅ Updated timestamps for {file_path}")
        # except subprocess.CalledProcessError as e:
            # logging.error(f"⚠️ Failed to update timestamps: {e}")

def load_cache():
    """Load cached video list to avoid unnecessary re-scanning."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save the video list cache."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

def get_all_videos():
    """Fetch video metadata from YouTube and save it to cache."""
    video_list = {}

    for channel in CHANNELS:
        logging.info(f"📡 Fetching video list from: {channel}")

        try:
            result = subprocess.run(
                ["yt-dlp", "--datebefore", "22000101", "--dump-json", channel],
                capture_output=True, text=True, check=True
            )

            channel_videos = []
            for line in result.stdout.splitlines():
                try:
                    video_data = json.loads(line)
                    channel_videos.append({
                        "title": video_data.get("title"),
                        "uploader": video_data.get("uploader", "UnknownUploader"),
                        "url": video_data.get("webpage_url"),
                        "upload_date": datetime.strptime(video_data.get("upload_date"), "%Y%m%d").isoformat()
                    })
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logging.error(f"⚠️ Skipping malformed video entry: {e}")

            video_list[channel] = channel_videos

        except subprocess.CalledProcessError as e:
            logging.error(f"⚠️ Failed to fetch video list for {channel}: {e}")

    # ✅ Save updated video list to cache
    save_cache(video_list)

    logging.info("✅ Video cache updated.")
    return video_list

def apply_upload_dates(video_path, upload_date):
    """Apply the correct upload date timestamp to a single downloaded video."""
    if not os.path.exists(video_path):
        logging.error(f"⚠️ File not found: {video_path}")
        return

    try:
        # force_correct_timestamps(video_path, upload_date)

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

def download_oldest_videos():
    """Ensure metadata is fetched, then download videos in chronological order."""
    update_yt_dlp()  # ✅ Ensure yt-dlp is up to date before downloading

    videos = load_cache()

    # ✅ If the cache is empty, fetch new video metadata
    if not videos:
        logging.info("⚠️ No cached videos found. Fetching video metadata...")
        videos = get_all_videos()

    if not videos:
        logging.info("⚠️ Still no videos found after fetching. Exiting.")
        return

    # ✅ Ensure videos are sorted by upload_date
    sorted_videos = []
    for channel, video_list in videos.items():
        sorted_videos.extend(video_list)
    sorted_videos.sort(key=lambda v: v["upload_date"])

    for video in sorted_videos:
        sanitized_title = sanitize_filename(video["title"])
        uploader_folder = os.path.join(BASE_DIRECTORY, video.get("uploader", "UnknownUploader"))
        video_path = os.path.join(uploader_folder, f"{video.get('uploader', 'UnknownUploader')} - {sanitized_title}.mp4")

        # ✅ Print the folder contents ONCE per session
        if uploader_folder not in printed_folders and os.path.exists(uploader_folder):
            logging.info(f"\n📂 Files in {uploader_folder}:")
            for filename in os.listdir(uploader_folder):
                logging.info(f" - {filename}")
            printed_folders.add(uploader_folder)

        # ✅ Print expected filename
        logging.info(f"🔍 Looking for: {video_path}")

        if not os.path.exists(video_path):
            logging.error(f"⚠️ File not found: {video_path}")
            continue

        try:
            upload_date = datetime.strptime(video["upload_date"], "%Y-%m-%dT%H:%M:%S")
            apply_upload_dates(video_path, upload_date)
        except ValueError as e:
            logging.error(f"⚠️ Error parsing upload date for {video['title']}: {e}")
            
    # sorted_videos = []
    # for channel, video_list in videos.items():
        # sorted_videos.extend(video_list)
    # sorted_videos.sort(key=lambda v: v["upload_date"])  # ✅ Sort by upload_date

    # for video in sorted_videos:  # ✅ Loop over sorted list
        # sanitized_title = sanitize_filename(video["title"])  # ✅ Apply sanitize_filename()
        # video_path = DOWNLOAD_PATH % {
            # "uploader": video.get("uploader", "UnknownUploader"),
            # "title": sanitized_title,
            # "ext": "mp4"
        # }

        # # ✅ Check if the video is already in downloaded.txt (avoid unnecessary downloads)
        # if os.path.exists(DOWNLOAD_ARCHIVE):
            # with open(DOWNLOAD_ARCHIVE, "r", encoding="utf-8") as f:
                # downloaded_videos = f.read()
            # if video["url"] in downloaded_videos:
                # logging.info(f"✅ Already downloaded (tracked in downloaded.txt): {video['title']}")
                # continue

        logging.info(f"📥 Downloading: {video['title']} ({video['upload_date']})")
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

        # for line in process.stdout:
            # logging.info(line.strip())
            # if "has already been recorded in the archive" in line:
                # already_in_archive = True  # ✅ Mark it as archived

        process.wait()

        if process.returncode != 0:
            logging.error(f"⚠️ Download failed for {video['title']} with exit code {process.returncode}")
            continue

        if not os.path.exists(video_path):
            logging.error(f"⚠️ File missing after download: {video_path}")

        # # ✅ Apply timestamps **only to the downloaded file**
        # upload_date = datetime.strptime(video["upload_date"], "%Y-%m-%dT%H:%M:%S")
        # apply_upload_dates(video_path, upload_date)

        # ✅ Skip sleep if yt-dlp reported "already in archive"
        if already_in_archive:
            logging.info("⏭️ Skipping sleep since video was already recorded in the archive.")
            continue
        
        # ✅ Skip sleep if the file was already found
        if os.path.exists(video_path):
            logging.info("⏭️ Skipping sleep since video file was already present.")
            continue
        
        # ✅ Add a manual sleep after full downloads (not merging)
        sleep_time = random.randint(30, 60)
        logging.info(f"⏳ Sleeping for {sleep_time} seconds before the next download...")
        time.sleep(sleep_time)  # ✅ Always runs, unless it's the last video
            
if __name__ == "__main__":
    download_oldest_videos()
    