import unittest
import os
import asyncio
from fastapi.testclient import TestClient
from ace.main import app
from ace import database
from ace.config import settings

class TestApiSecurity(unittest.TestCase):
    """
    Tests for the API security layer.
    """
    DB_PATH = "test_api_playbook.db"

    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment for the entire class.
        """
        settings['database'] = {
            'type': 'sqlite',
            'sqlite': {
                'path': cls.DB_PATH
            }
        }
        if os.path.exists(cls.DB_PATH):
            os.remove(cls.DB_PATH)

        asyncio.run(database.db_connect())
        asyncio.run(database.initialize_database())
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the test environment for the entire class.
        """
        asyncio.run(database.db_close())
        if os.path.exists(cls.DB_PATH):
            os.remove(cls.DB_PATH)

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
