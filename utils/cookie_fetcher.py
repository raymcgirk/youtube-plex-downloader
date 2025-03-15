import browser_cookie3
import os
import logging

COOKIES_PATH = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")

def fetch_cookies():
    """Fetches YouTube cookies from the default browser and saves them in Netscape format."""
    try:
        logging.info("🍪 Fetching fresh cookies from the browser...")
        cj = browser_cookie3.chrome(domain_name=".youtube.com")  # Change to `firefox()` if using Firefox

        # Save cookies in Netscape format
        with open(COOKIES_PATH, "w", encoding="utf-8") as f:
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in cj:
                f.write(f"{cookie.domain}\t{'TRUE' if cookie.domain.startswith('.') else 'FALSE'}\t{cookie.path}\t"
                        f"{'TRUE' if cookie.secure else 'FALSE'}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")

        logging.info(f"✅ Cookies saved to {COOKIES_PATH}")
    except Exception as e:
        logging.error(f"❌ Failed to fetch cookies: {e}")

if __name__ == "__main__":
    fetch_cookies()
