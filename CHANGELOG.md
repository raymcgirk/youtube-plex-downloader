# Changelog

## v1.3.0 (March 2025)
New Features
---
- Channel Thumbnail Downloads
  - Added support for downloading and storing YouTube channel profile pictures (folder.jpg).
  - Channel thumbnails are first downloaded to the staging folder, then moved to their respective Plex directories for better organization.
- Improved Filename Sanitization
 - Filenames now replace double quotes (") with full-width quotation marks (＂) to prevent issues on certain file systems.
---
Enhancements
- Refactored Logging and Handling
 - Improved log messages for clarity, especially in error handling.
 - More structured output for metadata embedding and file movement.
---
Bug Fixes
- Fixed Edge Cases in Metadata Handling
  - Additional checks ensure that metadata is embedded correctly, avoiding unnecessary reprocessing.
- Stabilized Video Processing Flow
  - Improved logic to prevent redundant metadata operations and better handle missing files.

---

## v1.2.1 - Hotfix (March 2025)
-  Added `config.json` (forgot in v1.2.0 🤦).
-  Updated documentation to clarify setup.

---

## v1.2.0 - Major Update: Staging Folder, Config Support, and Efficiency Boost (March 2025)
-  Now downloads to **STAGING** and moves to **PLEX** after processing.
-  **Fully dynamic `config.json`** removes hardcoded paths & channels.
-  **Optimized file checks** → instant skip for already downloaded videos.
-  **Moves all associated files** (mp4, jpg) together.
-  **Improved logging**: only logs important events, avoids bloat.
-  **Overall speed & efficiency massively improved.**

---

## v1.1.1 - Bug Fixes (March 2025)
-  Fixed logic that was skipping downloads incorrectly.
-  Improved handling of metadata checking.
-  Ensured metadata embedding only runs on existing files.

---

## v1.1.0 - Performance & Metadata Enhancements (March 2025)
-  Skips re-embedding metadata if it's already present (huge speed boost!)
-  Improved `ffprobe` handling to prevent JSON errors
-  Logs stored in `logs/` folder for better debugging
-  More robust filename sanitization
-  Automatic yt-dlp updates before downloads

---

## v1.0.0 - Initial Release (March 2025)
- First release! Basic functionality:
  - Downloads YouTube videos.
  - Stores them in Plex-friendly format.
  - Embeds metadata automatically.
