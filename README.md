# YouTube to Plex Downloader v2.0.0 🚀

## **Introduction**
The **YouTube to Plex Downloader** is a Python-based tool that automates the process of fetching metadata and downloading YouTube videos, organizing them for Plex compatibility. This version, **v2.0.0**, introduces significant improvements in caching, efficiency, and modularity.

## **What's New in v2.0.0?**

### **Major Updates:**
- **Reworked caching system** to prevent duplicate processing and improve efficiency.
- **SQLite-based tracking** of last downloaded videos per channel.
- **Batch processing for metadata caching** to reduce file I/O and improve speed.
- **Parallelized metadata fetching** to process multiple channels at the same time.
- **Converted from a single large `python` script into a modular system** with separate `.py` files for clarity and better file management.
- **Added automatic log purging to remove old logs and prevent unnecessary storage buildup.**

### **Improvements:**
- **Reduced redundant API calls** by skipping already cached videos.
- **Enhanced logging** to better debug yt-dlp command execution.
- **Refactored `fetcher.py` and `cache.py`** for scalability.
- **Logs now auto-delete after 30 days, reducing clutter and improving long-term efficiency.**

### **Fixes:**
- **Resolved issue where certain channels were skipped due to caching bugs.**
- **Fixed `yt-dlp` authentication issues** by ensuring proper cookie management.
- **Prevented unnecessary full cache rewrites** to improve performance.

### **Breaking Changes:**
- `video_cache.json` structure has changed; existing users may need to clear it.
- SQLite is now required for tracking previously downloaded videos.
- Users must provide fresh browser cookies when running on a new machine.

---

## **Installation Instructions**
### **Prerequisites**
Ensure you have the following installed:
- **Python 3.8+** (Recommended: Python 3.10+)
- **yt-dlp** (for video metadata and downloads)
- **SQLite** (for video tracking)
- **FFmpeg** (for video processing if needed)
- **pip packages:** `pip install -r requirements.txt`

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/youtube-plex-downloader.git
cd youtube-plex-downloader
```

### **2️⃣ Install Required Dependencies**
```bash
pip install -r requirements.txt
```

### **3️⃣ Configure Your Channels and Cookies**
- **Edit `config/config.json`** to include YouTube channels you want to download from.
- **Extract fresh cookies.txt** for authentication:
  ```bash
  yt-dlp --cookies-from-browser chrome --cookies cookies.txt
  ```
  *(Replace `chrome` with `firefox` or `edge` if needed.)*

### **4️⃣ Run the Fetcher Script**
```bash
python youtube/fetcher.py
```
This will fetch metadata and store it for future processing.

### **5️⃣ Run the Downloader**
```bash
python youtube/downloader.py
```
This will download the videos based on cached metadata.

---

## **How It Works**
1. **Metadata Fetching (`fetcher.py`)**
   - Retrieves video metadata from each channel.
   - Caches results in `video_cache.json` (short-term) and `video_tracking.db` (long-term tracking).
   - Uses parallel processing to speed up metadata collection.
   
2. **Video Downloading (`downloader.py`)**
   - Downloads videos **oldest to newest** based on cached metadata.
   - Once a channel is fully downloaded, it only fetches new videos.
   - Uses SQLite to track previously downloaded content, avoiding duplicate downloads.

---

## **Troubleshooting**
**Issue: `yt-dlp` fails due to missing `cookies.txt`?**  
✅ Ensure you've extracted fresh cookies and placed them in the project directory.

**Issue: Video metadata is not being fetched?**  
✅ Run `yt-dlp --flat-playlist --dump-json CHANNEL_URL` manually to check if YouTube is blocking access.

**Issue: Duplicates appearing in downloads?**  
✅ Ensure `video_cache.json` is not corrupted or try deleting it and re-running `fetcher.py`.

---

## **Contributing**
We welcome contributions! Feel free to submit pull requests or open issues on GitHub.

## **License**
This project is licensed under the MIT License.

## **Acknowledgments**
Special thanks to all contributors and testers who helped make **v2.0.0** a major upgrade! 🎉
