import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.worldnewsapi.com"
TOKEN = os.getenv("WORLDNEWS_API_KEY")

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1


def get_headlines_for_location(lat, lon):
    location_filter = f"{lat},{lon},50"
    params = {
        "api-key": TOKEN,
        "location-filter": location_filter,
        "language": "en",
        "number": 10,
    }

    data = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(f"{BASE_URL}/search-news", params=params)
            data = response.json()
            break  # got valid JSON back, stop retrying
        except (requests.exceptions.RequestException, ValueError) as e:
            # ValueError covers json.JSONDecodeError, in case a non-JSON
            # requests version doesn't classify it under RequestException.
            print(
                f"worldnewsapi request failed (attempt {attempt}/{MAX_ATTEMPTS}): {e!r}"
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

    if data is None:
        # Every attempt failed to return usable JSON (network error, empty
        # body, non-JSON error page, etc.). Fail gracefully instead of
        # raising, same pattern as services/flight.py.
        return {"success": False, "reason": "news_api_unavailable"}

    if data.get("status") == "failure":
        return {"success": False, "reason": "api_error"}

    articles = []

    for result in data["news"]:
        articles.append(
            {
                "title": result["title"],
                "text": result["text"],
                "url": result["url"],
                "publish_date": result["publish_date"],
            }
        )
    if not articles:
        return {"success": False, "reason": "no_articles_found"}
    return {"success": True, "articles": articles}
