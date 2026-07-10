import unittest
from services.db import save_search, get_cached_search, conn

class TestDb(unittest.TestCase):

    def tearDown(self):
        conn.execute("DELETE FROM searches WHERE flight_number LIKE 'TEST%'")
        conn.commit()

    def test_save_and_retrieve(self):
        destination = {"city": "Testville", "state": "TS", "country": "TS", "lat": 1.0, "lon": 2.0}
        articles = [{"title": "Test article", "category": "general update"}]

        save_search("TEST123", destination, "A test summary", articles)
        cached = get_cached_search("TEST123")

        self.assertIsNotNone(cached)
        self.assertEqual(cached["city"], "Testville")
        self.assertEqual(cached["summary"], "A test summary")

    def test_cache_miss_returns_none(self):
        result = get_cached_search("TEST_DOES_NOT_EXIST")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
