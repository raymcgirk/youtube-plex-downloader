import subprocess
import logging

def update_yt_dlp():
    logging.info("🔄 Checking for yt-dlp updates...")
    subprocess.run(["yt-dlp", "-U"], check=False)
