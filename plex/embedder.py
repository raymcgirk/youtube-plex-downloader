import os
import json
import subprocess
import logging

def has_existing_metadata(video_path, upload_date):
    """Check if the video file already has the correct upload date metadata."""
    if not os.path.exists(video_path):
        logging.warning(f"⚠️ File not found: {video_path}. Skipping metadata check.")
        return False

    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_entries", "format_tags", video_path],
            capture_output=True, text=True, encoding="utf-8", check=False
        )

        if result.returncode != 0 or not result.stdout.strip():
            logging.warning(f"⚠️ ffprobe issue or no metadata for {video_path}")
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
        return  # Skip processing if metadata is already correct

    try:
        formatted_plex_date = upload_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Clearly define the temporary output file explicitly here
        temp_video_path = video_path.replace(".mp4", "_temp.mp4")

        # Embed metadata using FFmpeg
        subprocess.run([
            "ffmpeg", "-i", video_path,
            "-metadata", f"date={formatted_plex_date}",
            "-metadata", f"originally_available={formatted_plex_date}",
            "-codec", "copy",
            temp_video_path
        ], check=True)

        os.replace(temp_video_path, video_path)
        logging.info(f"✅ Embedded metadata into {video_path}")

    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ Failed to embed metadata for {video_path}: {e}")

    except Exception as e:
        logging.error(f"⚠️ Unexpected error embedding metadata for {video_path}: {e}")
