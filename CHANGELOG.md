# Changelog

## v1.1.0 - Performance & Metadata Enhancements (March 2025)
-  Skips re-embedding metadata if it's already present (huge speed boost!)
-  Improved `ffprobe` handling to prevent JSON errors
-  Logs stored in `logs/` folder for better debugging
-  More robust filename sanitization
-  Automatic yt-dlp updates before downloads

## v1.0.0 - Initial Release (March 2025)
- First release! Basic functionality:
  - Downloads YouTube videos.
  - Stores them in Plex-friendly format.
  - Embeds metadata automatically.
