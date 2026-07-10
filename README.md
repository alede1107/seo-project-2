# FlightScope

FlightScope is a Flask app that lets a user enter an active flight number and see local news for the flight's destination. The app looks up the active flight, finds the arrival airport, searches for nearby news, uses Gemini to classify and summarize local articles, and renders the results in a web page.

## Features

- Search by flight number from the home page.
- Looks up active flight data with Aviationstack.
- Maps arrival airport codes to city, state, country, latitude, and longitude.
- Fetches local news near the destination with WorldNewsAPI.
- Uses Gemini to filter local articles, categorize them, and create a destination summary.
- Caches recent searches in SQLite for 15 minutes.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
AVIATIONSTACK_API_KEY=your_aviationstack_key
WORLDNEWS_API_KEY=your_worldnewsapi_key
GEMINI_API_KEY=your_gemini_key
```

## Run

Start the Flask app:

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5001/
```

Enter an active flight number such as `AA100`, `DL9483`, or another currently active flight.

## How It Works

1. `GET /` renders the search form.
2. `POST /results` reads `flight_number` from the form.
3. The app checks the SQLite cache for a recent matching search.
4. If there is no cache hit, it calls Aviationstack to find the active flight destination.
5. It calls WorldNewsAPI for local articles near the destination coordinates.
6. It calls Gemini through `classify_articles()` to filter, categorize, and summarize articles.
7. It saves successful results to `flightscope.db` and renders `templates/results.html`.

## Project Structure

```text
app.py                     Flask routes and page flow
requirements.txt           Python dependencies
static/style.css           App styling
templates/index.html       Search page
templates/results.html     Results page
services/flight.py         Aviationstack flight lookup
services/news.py           WorldNewsAPI local news lookup
services/classifier.py     Gemini article classifier and summarizer
services/db.py             SQLite cache
services/data/airports.json Airport metadata
tests/                     Service tests
```

## Troubleshooting

`Not Found` on `/` usually means the Flask server is not running the current `app.py` or you are on the wrong port. This app runs on port `5001`.

`We couldn't find an active flight` means Aviationstack did not return a currently active flight for that flight number. Try a different live flight.

`We found your flight, but couldn't load local news right now` can mean WorldNewsAPI failed, Gemini failed, or Gemini quota was exceeded. Check the terminal output for the exact API error.

If Gemini returns `429 RESOURCE_EXHAUSTED`, the API key has hit its quota. Wait for quota reset, use another project/key, or increase quota.

## Notes

- `.env`, log files, Python cache files, and `flightscope.db` are ignored by git.
- Flight activity changes quickly, so a flight number that works now may fail later.
