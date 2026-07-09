from flask import Flask, jsonify, render_template, request
from requests.exceptions import RequestException

from services.flight import get_destination_from_flight
from services.news import get_headlines_for_location


app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/results")
def results():
    flight_number = request.form.get("flight_number", "").strip()

    if not flight_number:
        return render_template("index.html", error="Please enter a flight number.")

    try:
        destination = get_destination_from_flight(flight_number)
    except RequestException:
        return render_template(
            "results.html",
            success=False,
            flight_number=flight_number,
            stage="flight",
            reason="flight_api_unavailable",
        )

    if not destination.get("success"):
        return render_template(
            "results.html",
            success=False,
            flight_number=flight_number,
            stage="flight",
            reason=destination.get("reason"),
        )

    try:
        headlines = get_headlines_for_location(destination["lat"], destination["lon"])
    except RequestException:
        return render_template(
            "results.html",
            success=False,
            flight_number=flight_number,
            stage="news",
            reason="news_api_unavailable",
        )

    if not headlines.get("success"):
        return render_template(
            "results.html",
            success=False,
            flight_number=flight_number,
            stage="news",
            reason=headlines.get("reason"),
        )

    try:
        from services.classifier import classify_articles

        classified = classify_articles(headlines["articles"], destination["city"])
    except Exception:
        return render_template(
            "results.html",
            success=False,
            flight_number=flight_number,
            stage="news",
            reason="classifier_unavailable",
        )

    if not classified.get("success"):
        return render_template(
            "results.html",
            success=False,
            flight_number=flight_number,
            stage="news",
            reason=classified.get("reason"),
        )

    return render_template(
        "results.html",
        success=True,
        flight_number=flight_number,
        destination=destination,
        articles=classified["articles"],
    )


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
    app.run(host="0.0.0.0", port=5001, debug=True)
