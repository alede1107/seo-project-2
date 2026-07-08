import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.worldnewsapi.com"
TOKEN = os.getenv("WORLDNEWS_API_KEY")


def get_headlines_for_location(lat, lon):
    location_filter = f"{lat},{lon},50"
    params = {
        "api-key": TOKEN,
        "location-filter": location_filter,
        "language": "en",
        "number": 10,
    }

    response = requests.get(f"{BASE_URL}/search-news", params=params)
    data = response.json()

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
