# YouTube to Plex Downloader v2.0.1 🚀

## **Introduction**
The **YouTube to Plex Downloader** is a Python-based tool that automates the process of fetching metadata and downloading YouTube videos, organizing them for Plex compatibility. This version, **v2.0.1**, introduces significant improvements in caching, efficiency, and modularity.

## **What's New in v2.0.1?**

### **Major Updates:**
- **Reworked Fetching & Processing:**
  - Videos are now processed **one at a time** instead of batch-fetching metadata.
  - Prevents YouTube rate-limiting and reduces the risk of getting blocked.

- **Resumable Downloads Enabled:**
  - Removed `--no-part`, so interrupted downloads now resume from the last completed part.
  - Videos no longer restart from 0% if the download is interrupted.

- **Increased Download Speed:**
  - **Boosted from 2MB/s → 5MB/s** (150% faster) while avoiding rate limits.

- **Improved File Movement & Cleanup:**
  - **Fixed colon (`:`) issues** in filenames using `sanitize_filename()`.
  - **Thumbnails (`.jpg`) are now deleted automatically** after embedding metadata.
  - **Files now move correctly to Plex**, ensuring proper organization.

- **Enhanced Logging System:**
  - Added **separate logging for `yt-dlp`** in `logs/yt-dlp-debug_YYYY-MM-DD.log`.
  - **Old logs (30+ days) are automatically purged**, preventing clutter.
  - **Increased visibility of file movement & metadata embedding.**

### **Fixes:**
- **Resolved issue where certain videos were not detected as downloaded.**
- **Fixed script failing to move files after download.**
- **Fixed unnecessary sleep timer when videos were already downloaded.**
- **Prevented yt-dlp’s filename changes from breaking Plex organization.**
- **Ensured Plex folder paths are set up correctly to avoid missing files.**

### **Breaking Changes:**
- **Removed SQLite dependency**; all metadata is now stored in `video_cache.json`.
- **Fetching logic changed** to prevent YouTube from blocking requests.

---

## **Installation Instructions**
### **Prerequisites**
Ensure you have the following installed:
- **Python 3.8+** (Recommended: Python 3.10+)
- **yt-dlp** (for video metadata and downloads)
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
   - Caches results exclusively in `video_cache.json` (SQLite removed).
   - Processes videos one at a time to prevent YouTube rate limits.
   
2. **Video Downloading (`downloader.py`)**
   - Downloads videos **oldest to newest** based on cached metadata.
   - Once a channel is fully downloaded, it only fetches new videos.
   - Automatically embeds metadata and moves files to Plex.

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
Special thanks to all contributors and testers who helped make **v2.0.1** a major upgrade! 🎉
