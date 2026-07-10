import unittest
from unittest.mock import patch, MagicMock
from services.flight import get_destination_from_flight


class TestFlight(unittest.TestCase):

    @patch("services.flight.requests.get")
    def test_active_flight_returns_destination(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"flight_status": "active", "arrival": {"iata": "JFK"}}]
        }
        mock_get.return_value = mock_response

        result = get_destination_from_flight("AA100")

        self.assertTrue(result["success"])
        self.assertEqual(result["city"], "New York")

    @patch("services.flight.requests.get")
    def test_no_active_flight_returns_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"flight_status": "scheduled", "arrival": {"iata": "JFK"}}]
        }
        mock_get.return_value = mock_response

        result = get_destination_from_flight("AA100")

        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "no_active_flight")

    @patch("services.flight.requests.get")
    def test_airport_not_in_database(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"flight_status": "active", "arrival": {"iata": "ZZZZ"}}]
        }
        mock_get.return_value = mock_response

        result = get_destination_from_flight("AA100")

        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "airport_not_in_database")


if __name__ == "__main__":
    unittest.main()
