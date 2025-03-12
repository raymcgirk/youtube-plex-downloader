# 📥 YouTube to Plex Downloader

A fully automated **YouTube video downloader** that:
- 📂 **Downloads videos to a staging folder** before moving them to **Plex**.
- ⚡ **Skips already downloaded videos** for maximum efficiency.
- 🛠️ **Supports metadata embedding** (so Plex displays videos correctly).
- 🔍 **Configurable via `config.json`**—no need to modify the script!

---

## 🚀 Features
- ✅ **Efficient file handling** (no duplicate downloads).
- 📂 **Automatic organization** (moves files after processing).
- 🔄 **Dynamic `config.json`**—fully customizable paths & channels.
- 🎯 **Supports thumbnails, metadata, and proper Plex formatting**.
- 🔥 **Fast and optimized logging**—only logs important details.

---

## 📦 Installation
### **1️⃣ Install Required Dependencies**
Ensure you have:
- **Python 3** (Download: [python.org](https://www.python.org/))
- **yt-dlp** for YouTube downloads:
  ```sh
  pip install yt-dlp
- ffmpeg for metadata embedding [Download](https://ffmpeg.org/download.html)
