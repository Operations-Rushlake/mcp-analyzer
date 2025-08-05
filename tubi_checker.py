import requests
from bs4 import BeautifulSoup

SCRAPERAPI_KEY = "5da6a435c89f56b1ef3f4541d2c6d9bc"

def check_tubi_streaming(tubi_url, territory="United States"):
    country_code = {
        "United States": "us",
        "Canada": "ca",
        "United Kingdom": "gb"
        # Add more mappings if needed
    }.get(territory, "us")

    headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # *** KEY CHANGE HERE: ADD &render=true ***
    proxy_url = (
        f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}"
        f"&url={tubi_url}&country_code={country_code}&render=true"
    )

    print(f"Attempting to fetch with JavaScript rendering: {proxy_url}")

    try:
        response = requests.get(proxy_url, headers=headers, timeout=60) # Increased timeout further, rendering can take longer
        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        return {"error": f"Failed to fetch page: Read timed out after 60 seconds (with rendering). {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch page: Network or HTTP error (with rendering). {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred (with rendering): {str(e)}"}

    try:
        with open("debug_tubi_response_rendered.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved RENDERED HTML response to debug_tubi_response_rendered.html")
    except Exception as e:
        print(f"Warning: Could not save debug HTML file: {e}")

    html_content_lower = response.text.lower()

    # --- REVISED KEYWORDS (based on typical rendered player elements) ---
    # After rendering, the <video> tag should be present, along with player controls.
    keywords = [
        '<video',                                     # The HTML5 video tag
        'data-qa="player-container"',                # Common attribute for player containers
        'aria-label="play video"',                   # Common accessibility label for play button
        'aria-label="pause video"',                  # Common accessibility label for pause button
        'class="jw-video jw-reset"',                 # Potential class for JW Player (often used)
        'class="vjs-tech"',                          # Potential class for Video.js player
        'class="player-overlay"',                    # A common class for a player overlay
        'class="player-controls"',                   # Class for the control bar
        'current-time',                              # Presence of time display
        'duration',                                  # Presence of total duration display
        'fullscreen-button',                         # Name for fullscreen button
        'volume-button'                              # Name for volume button
    ]

    is_available = any(keyword.lower() in html_content_lower for keyword in keywords)

    return {
        "url": tubi_url,
        "territory": territory,
        "available": is_available,
        "status_code": response.status_code
    }

# Example usage for testing
if __name__ == "__main__":
    test_url = "https://tubitv.com/movies/100039682/boda-love"
    print(f"Checking Tubi URL with rendering: {test_url}")
    result = check_tubi_streaming(test_url, "United States")
    print(result)