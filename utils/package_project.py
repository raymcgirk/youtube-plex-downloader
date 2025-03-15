import os
import logging
import zipfile
from pathlib import Path

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# Move up to the project root explicitly
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]  # Move TWO levels up from utils/
logging.debug(f"PROJECT_ROOT resolved to: {PROJECT_ROOT}")

# Define distribution directory
DIST_DIR = PROJECT_ROOT / "dist"
DIST_DIR.mkdir(exist_ok=True)  # Ensure dist directory exists
ZIP_NAME = DIST_DIR / "YouTube-Plex-Downloader-v2.0.1.zip"

def get_gitignore_patterns():
    """Read .gitignore and return a list of patterns to ignore, ensuring .git/ is always ignored."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    logging.debug(f"Reading .gitignore from: {gitignore_path}")

    ignore_patterns = [".git/"]  # Ensure .git/ is always ignored

    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            ignore_patterns += [line.strip() for line in f if line.strip() and not line.startswith("#")]

    logging.debug(f"Loaded ignore patterns from .gitignore: {ignore_patterns}")
    return ignore_patterns

def should_ignore(file_path, ignore_patterns):
    """Check if a file or directory should be ignored based on .gitignore patterns."""
    file_path = Path(file_path).resolve()  # Ensure absolute path
    relative_path = file_path.relative_to(PROJECT_ROOT.resolve())  # Fix path issue
    logging.debug(f"Checking if should ignore: {relative_path}")

    for pattern in ignore_patterns:
        if relative_path.match(pattern) or str(relative_path).startswith(pattern.rstrip('/')):
            logging.debug(f"⏩ Skipping: {relative_path} (matches {pattern})")
            return True  # Skip ignored files and directories

    return False

def zip_project():
    ignore_patterns = get_gitignore_patterns()

    logging.info(f"📦 Creating ZIP: {ZIP_NAME}")

    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(PROJECT_ROOT):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, PROJECT_ROOT)

                if should_ignore(file_path, ignore_patterns):
                    logging.info(f"⏩ Skipping ignored file/directory: {relative_path}")
                    continue  # Skip ignored files

                logging.info(f"📂 Adding file: {relative_path}")
                zipf.write(file_path, relative_path)

    logging.info(f"✅ Project packaged as {ZIP_NAME}")

if __name__ == "__main__":
    zip_project()
