import os
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ZIP_NAME = PROJECT_ROOT / "YouTube-Plex-Downloader-v2.0.1.zip"


def get_gitignore_patterns():
    """Read .gitignore and return a list of patterns to ignore."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if not gitignore_path.exists():
        return []

    with open(gitignore_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def should_ignore(file_path, ignore_patterns):
    """Check if a file should be ignored based on .gitignore patterns."""
    return any(Path(file_path).match(pattern) for pattern in ignore_patterns)


def zip_project():
    ignore_patterns = get_gitignore_patterns()

    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(PROJECT_ROOT):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, PROJECT_ROOT)

                if should_ignore(relative_path, ignore_patterns):
                    continue  # Skip ignored files

                zipf.write(file_path, relative_path)

    print(f"✅ Project packaged as {ZIP_NAME}")


if __name__ == "__main__":
    zip_project()
