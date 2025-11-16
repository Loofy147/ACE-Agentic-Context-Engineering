import unittest
import os
import asyncio
from fastapi.testclient import TestClient
from ace.main import app

from ace import database

class TestApiSecurity(unittest.TestCase):
    """Tests for the API security layer."""

    def setUp(self):
        """Set up the test client."""
        database.DATABASE_PATH = "test_api_playbook.db"
        asyncio.run(database.initialize_database())
        self.client = TestClient(app)

    def tearDown(self):
        """Remove the test database after each test."""
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_no_api_key(self):
        """Tests that a request without an API key is rejected."""
        response = self.client.get("/playbook/")
        self.assertEqual(response.status_code, 403)

    def test_invalid_api_key(self):
        """Tests that a request with an invalid API key is rejected."""
        response = self.client.get("/playbook/", headers={"X-API-Key": "invalid-key"})
        self.assertEqual(response.status_code, 401)

    def test_valid_api_key(self):
        """Tests that a request with a valid API key is accepted."""
        response = self.client.get("/playbook/", headers={"X-API-Key": "test-key-1"})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
