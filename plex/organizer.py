import shutil
import os
import logging

def organize_files(video: dict, staging_directory: str, plex_directory: str, sanitized_title: str):
    uploader = str(video.get("uploader", "UnknownUploader"))
    sanitized_title = str(sanitized_title)

    # Define staging and final directories clearly
    uploader_folder = os.path.join(staging_directory, uploader)
    final_uploader_folder = os.path.join(plex_directory, uploader)

    # Create final uploader directory if it doesn't exist
    if not os.path.exists(final_uploader_folder):
        os.makedirs(final_uploader_folder, exist_ok=True)

    # Move all related files (video, thumbnails, metadata) clearly and explicitly
    expected_prefix = f"{uploader} - {sanitized_title}"
    files_moved = False

    for file in os.listdir(uploader_folder):
        if file.startswith(expected_prefix):
            source_path = os.path.join(uploader_folder, file)
            destination_path = os.path.join(final_uploader_folder, file)

            if os.path.exists(source_path):
                shutil.move(source_path, destination_path)
                logging.info(f"✅ Moved {file} to Plex: {destination_path}")
                files_moved = True
            else:
                logging.error(f"⚠️ File not found for moving: {source_path}")

    # Clearly confirm if main video file moved successfully
    final_video_path = os.path.join(final_uploader_folder, f"{uploader} - {sanitized_title}.mp4")
    if files_moved and os.path.exists(final_video_path):
        logging.info(f"🎬 Video successfully moved to Plex: {final_video_path}")
    else:
        logging.warning(f"⚠️ No files were moved for video: {final_video_path}")
