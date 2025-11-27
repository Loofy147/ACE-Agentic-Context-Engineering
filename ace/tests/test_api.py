import unittest
import os
import asyncio
from fastapi.testclient import TestClient
from ace.main import app
from ace import database

class TestApiSecurity(unittest.TestCase):
    """
    Tests for the API security layer.

    This test suite ensures that the API endpoints are properly secured with
    API key authentication. It checks that requests without a valid API key
    are rejected, and requests with a valid key are accepted.
    """

    def setUp(self):
        """
        Set up the test environment.

        Initializes a test database and a TestClient for the FastAPI app.
        """
        database.DATABASE_PATH = "test_api_playbook.db"
        asyncio.run(database.initialize_database())
        self.client = TestClient(app)

    def tearDown(self):
        """
        Clean up the test environment.

        Removes the test database file after each test.
        """
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)

    def test_no_api_key(self):
        """
        Tests that a request without an API key is rejected with a 401 error.
        """
        response = self.client.get("/playbook/")
        self.assertEqual(response.status_code, 401)

    def test_invalid_api_key(self):
        """
        Tests that a request with an invalid API key is rejected with a 401 error.
        """
        response = self.client.get("/playbook/", headers={"X-API-Key": "invalid-key"})
        self.assertEqual(response.status_code, 401)

    def test_valid_api_key(self):
        """
        Tests that a request with a valid API key is accepted with a 200 status.
        """
        response = self.client.get("/playbook/", headers={"X-API-Key": "test-key-1"})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
