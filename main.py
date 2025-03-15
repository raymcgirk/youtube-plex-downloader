from config.loader import load_config
from logger.logger import setup_logger
from youtube.fetcher import get_all_videos
from youtube.utils import update_yt_dlp

def main():
    load_config()
    setup_logger()
    update_yt_dlp()
    get_all_videos()

if __name__ == "__main__":
    main()
