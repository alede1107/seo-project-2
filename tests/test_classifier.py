import unittest
import json
from unittest.mock import patch, MagicMock
from services.classifier import classify_articles


class TestClassifier(unittest.TestCase):

    @patch("services.classifier.client.models.generate_content")
    def test_filters_non_local_and_excluded(self, mock_generate):
        articles = [
            {"title": "Local weather", "url": "http://a", "text": "rain", "publish_date": "2026-07-09"},
            {"title": "National story", "url": "http://b", "text": "unrelated", "publish_date": "2026-07-09"},
            {"title": "Graphic crime", "url": "http://c", "text": "bad stuff", "publish_date": "2026-07-09"},
        ]
        fake_response = MagicMock()
        fake_response.text = json.dumps({
            "overall_summary": "Test summary of the city.",
            "articles": [
                {"index": 0, "is_local": True, "category": "weather", "exclude": False, "summary": "Rain expected."},
                {"index": 1, "is_local": False, "category": "general update", "exclude": False, "summary": "n/a"},
                {"index": 2, "is_local": True, "category": "concern", "exclude": True, "summary": "n/a"},
            ]
        })
        mock_generate.return_value = fake_response

        result = classify_articles(articles, "Detroit")

        self.assertTrue(result["success"])
        self.assertEqual(len(result["articles"]), 1)
        self.assertEqual(result["articles"][0]["title"], "Local weather")
        self.assertEqual(result["summary"], "Test summary of the city.")

    @patch("services.classifier.client.models.generate_content")
    def test_all_filtered_returns_failure(self, mock_generate):
        articles = [{"title": "Unrelated story", "url": "http://a", "text": "x", "publish_date": "2026-07-09"}]
        fake_response = MagicMock()
        fake_response.text = json.dumps({
            "overall_summary": "Nothing local found.",
            "articles": [
                {"index": 0, "is_local": False, "category": "general update", "exclude": False, "summary": "n/a"},
            ]
        })
        mock_generate.return_value = fake_response

        result = classify_articles(articles, "Detroit")

        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "no_local_articles")


if __name__ == "__main__":
    unittest.main()
