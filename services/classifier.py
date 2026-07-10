from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
import time

load_dotenv()

client = genai.Client()

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2


def classify_articles(articles, city):
    article_list = "\n\n".join(
        f"[{i}] Title: {a['title']}\nText: {a['text'][:500]}"
        for i, a in enumerate(articles)
    )
    prompt = f"""You are sorting news articles for a travel app. A user is flying to {city}.
    Below is a numbered list of articles. For each one, decide:

    1. is_local: true if the article is genuinely ABOUT {city} (local event, local story, something specific to that place) — false if it merely mentions {city} in passing while being a national/global/unrelated story.
    2. category: one of "concern", "local interest", "weather", "general update" — only if is_local is true.
    3. exclude: true if the article contains extremely graphic violence (informative news about violence is allowed), is highly politically inflammatory, or otherwise inappropriate for a general travel-news feed — regardless of is_local.

    Articles:
    {article_list}

    Return your answer as a JSON list, one object per article, in the same order, with fields: index, is_local, category, exclude."""

    response = None
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            break  # got a response, stop retrying
        except Exception as e:
            last_error = e
            print(
                f"gemini request failed (attempt {attempt}/{MAX_ATTEMPTS}): {e!r}"
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

    if response is None:
        # Every attempt failed (e.g. persistent 503 overload). Re-raise so
        # app.py's existing try/except around classify_articles catches it
        # and renders the normal "classifier_unavailable" error page
        # instead of crashing.
        raise last_error

    judgements = json.loads(response.text)

    results = []

    for judgement in judgements:
        if not judgement["is_local"] or judgement["exclude"]:
            continue
        article = articles[judgement["index"]]
        results.append(
            {
                "title": article["title"],
                "url": article["url"],
                "text": article["text"],
                "publish_date": article["publish_date"],
                "category": judgement["category"],
            }
        )
    if not results:
        return {"success": False, "reason": "no_local_articles"}
    return {"success": True, "articles": results}
