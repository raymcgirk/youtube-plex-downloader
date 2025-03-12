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
ffmpeg for metadata embedding [Download](https://ffmpeg.org/download.html)

---

### **2️⃣ Clone the Repository
    git clone https://github.com/YOUR_GITHUB_USERNAME/youtube-plex-downloader.git
    cd youtube-plex-downloader
---

### **3️⃣ Set Up config.json
Edit config.json to set up your file paths and YouTube channels:

    {
        "staging_directory": "PATH/TO/STAGING",
        "plex_directory": "PATH/TO/PLEX",
        "download_archive": "PATH/TO/DOWNLOAD_ARCHIVE",
        "cache_file": "PATH/TO/CACHE_FILE",
        "channels": [
            {"url": "https://www.youtube.com/@BobbyBroccoli", "enabled": true},
            {"url": "https://www.youtube.com/@Kurzgesagt", "enabled": false}
        ]
    }

---

### **4️⃣ Run the Script
      python youtube_plex_downloader.py

---

## ⚠️ Important Notes
- Modify config.json instead of editing the script directly.
- Ensure config.json is not uploaded with personal paths.
- Keep ffmpeg installed to embed metadata properly.
- If a video already exists, it will be skipped automatically.

---

## 🎉 Credits
Built by Shawn McCarthy
Uses yt-dlp for downloading.
Inspired by Plex automation workflows.

---

## 📜 License
Licensed under the MIT License. See LICENSE for details.
