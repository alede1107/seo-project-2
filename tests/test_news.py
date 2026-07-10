import unittest
from unittest.mock import patch, MagicMock
from services.news import get_headlines_for_location


class TestNews(unittest.TestCase):

    @patch("services.news.requests.get")
    def test_successful_headlines(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "news": [{
                "title": "Test headline",
                "text": "Some article text",
                "url": "http://example.com",
                "publish_date": "2026-07-09",
            }]
        }
        mock_get.return_value = mock_response

        result = get_headlines_for_location(40.6, -73.7)

        self.assertTrue(result["success"])
        self.assertEqual(len(result["articles"]), 1)
        self.assertEqual(result["articles"][0]["title"], "Test headline")

    @patch("services.news.requests.get")
    def test_error_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "failure", "code": 429, "message": "Too many requests",
        }
        mock_get.return_value = mock_response

        result = get_headlines_for_location(40.6, -73.7)

        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "api_error")

    @patch("services.news.requests.get")
    def test_empty_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"news": []}
        mock_get.return_value = mock_response

        result = get_headlines_for_location(40.6, -73.7)

        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "no_articles_found")


if __name__ == "__main__":
    unittest.main()
