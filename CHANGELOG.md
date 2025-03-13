# Changelog

## V1.3.5 - Stability & Major Bug Fixes  (March 12, 2025) 
### Critical Fixes
Fixed _latest Setting Too Early, Causing Skipped Videos
- Issue: _latest was being set as soon as caching started, meaning if the script was interrupted, it would skip videos on the next run.
- Fix: Introduced _in_progress, which tracks the last processed video.
 - _latest is only updated when all videos are cached, ensuring the script never skips videos after an interruption.
 - This means no more deleting video_cache.json due to bad _latest values—progress is always saved correctly.
### yt-dlp Enhancements
Prevented Hanging on Member-Only & Live Videos
- Issue: The script would get stuck on member-only videos, requiring manual intervention.
- Fix: Updated yt-dlp to automatically skip member-only and live videos using:

      --match-filter "!is_live & availability!=needs_auth"
  - Now, restricted videos are ignored completely, preventing unnecessary stalls.
  - No more manual intervention needed—the script runs cleanly from start to finish.
### Updated Timeout Handling for Stuck Videos
- Fixed an issue where yt-dlp could hang indefinitely on some videos.
- Now waits up to 60 seconds for a response before assuming a video is stuck.
- If no output for 60 seconds, the script:
 - Retries once.
 - If it hangs again, it skips the video and moves on.
- Logs the exact video title & URL when skipping, so stuck videos can be reviewed manually.
### Expected Behavior After Fixes
-  Caching now correctly tracks progress and resumes safely.
-  _latest is only updated when all videos have been cached, eliminating bad cutoff dates.
-  Member-only & live videos are automatically skipped, preventing script hangs.
-  Valid slow videos still process correctly.
-  Truly stuck videos no longer block the script indefinitely.
-  If a video gets skipped, it’s logged with its title & URL for review.

---

## v1.3.4 - Real-Time Cache Updates & Logging Fixes (March 12, 2025)
### Bug Fixes & Optimizations
- Real-time cache updates: The script now saves each video immediately after processing, instead of waiting for the entire channel to finish.
- Fixed a bug where all channels were processed before writing in blocks of 10. This caused unnecessary delays, especially for large channels with thousands of videos.
- Improved logging for channels with no new videos: The script now explicitly logs a warning if a channel has no new videos to download, avoiding confusion about whether it was skipped or failed.
- Increased crash resistance: If yt-dlp crashes or is interrupted, all videos up to that point are preserved in video_cache.json, preventing unnecessary re-fetching.
### Notes
- Writing every video immediately ensures no progress is lost if the script stops unexpectedly.
- If disk write performance becomes an issue, future updates may introduce batched writes (e.g., every 10 videos).
- The script is now fully crash-resistant and handles large channels more efficiently.

---

## v1.3.3 - Incremental Cache Saves & Logging Improvements (March 12, 2025)
### Bug Fixes & Optimizations
- Incremental cache updates: The script now saves the cache every 10 videos instead of waiting for the entire channel to be processed. This prevents data loss if the script crashes mid-fetch.
- Improved crash resilience: In the event of an error or interruption, the script now resumes from the last saved state, preventing unnecessary re-fetching of thousands of videos.
- More accurate logging for missing videos: Instead of logging a critical error when no new videos are found, the script now issues a warning with clear messaging, distinguishing between an actual failure and an expected case where no new videos are available.
- Final save per channel: Ensures that even if a channel has fewer than 10 videos, its progress is still committed to video_cache.json.

### Notes
- This update greatly improves efficiency for large channels with thousands of videos.
- The new caching method ensures minimal progress loss in case of unexpected shutdowns.

---

## v1.3.2 - Hotfix for New Channel Detection (March 12, 2025)
### Bug Fixes
- Fixed an issue where newly enabled channels were not being detected properly and did not fetch videos.
- The script now correctly updates video_cache.json when a new channel is added, ensuring new videos are downloaded without affecting existing cached data.
- Improved logging clarity for new channel fetching to ensure correct debugging and monitoring.
### Notes
- This is a hotfix to address a bug introduced in v1.3.1. No new features have been added.
- The script now functions as expected when enabling additional channels and dynamically pulls new content.

---

## v1.3.1 - Bug Fixes & Optimizations (March 12, 2025)

### Bug Fixes
- Fixed an issue where only one channel was downloading due to caching not updating correctly.
- Resolved a bug where video_cache.json incorrectly stored _latest entries, causing crashes when iterating over channels.
- Prevented the script from attempting to download thumbnails every time it runs by checking if folder.jpg already exists in the Plex directory.
- Fixed logging order so that the script correctly logs when it is checking for a thumbnail before attempting a download.
- Corrected an issue where the script was using the channel URL name (streetscaping) instead of the actual channel name (Streetscapes) for organizing files.
- Fixed a bug where yt-dlp was hanging when attempting to extract the uploader name from the channel page; now correctly extracts it from the latest video.
### Optimizations
- Improved cache handling to ensure that new videos are fetched without re-caching everything.
- Optimized the thumbnail download process to prevent redundant operations.
- Adjusted the script to handle errors more gracefully when yt-dlp encounters unexpected issues.
- Ensured that logging is now clear, sequential, and informative.
### Notes
- Future feature requests (e.g., limiting downloads to the last X videos or videos after a certain date) would be considered for a future minor release.

---

## v1.3.0 (March 2025)
### New Features
- Channel Thumbnail Downloads
  - Added support for downloading and storing YouTube channel profile pictures (folder.jpg).
  - Channel thumbnails are first downloaded to the staging folder, then moved to their respective Plex directories for better organization.
- Improved Filename Sanitization
 - Filenames now replace double quotes (") with full-width quotation marks (＂) to prevent issues on certain file systems.
### Enhancements
- Refactored Logging and Handling
 - Improved log messages for clarity, especially in error handling.
 - More structured output for metadata embedding and file movement.
### Bug Fixes
- Fixed Edge Cases in Metadata Handling
  - Additional checks ensure that metadata is embedded correctly, avoiding unnecessary reprocessing.
- Stabilized Video Processing Flow
  - Improved logic to prevent redundant metadata operations and better handle missing files.

---

## v1.2.1 - Hotfix (March 2025)
-  Added `config.json` (forgot in v1.2.0).
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
