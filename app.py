from flask import Flask, jsonify
from requests.exceptions import RequestException

from services.flight import get_destination_from_flight
from services.news import get_headlines_for_location


app = Flask(__name__)


@app.get("/flight/<flight_number>/news")
def flight_news(flight_number):
    try:
        destination = get_destination_from_flight(flight_number)
    except RequestException:
        return (
            jsonify(
                {
                    "success": False,
                    "stage": "flight",
                    "reason": "flight_api_unavailable",
                }
            ),
            502,
        )

    if not destination.get("success"):
        return jsonify({"success": False, "stage": "flight", **destination}), 404

    try:
        headlines = get_headlines_for_location(destination["lat"], destination["lon"])
    except RequestException:
        return (
            jsonify(
                {
                    "success": False,
                    "stage": "news",
                    "reason": "news_api_unavailable",
                }
            ),
            502,
        )

    if not headlines.get("success"):
        return jsonify({"success": False, "stage": "news", **headlines}), 502

    return jsonify(
        {
            "success": True,
            "destination": destination,
            "articles": headlines["articles"],
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
