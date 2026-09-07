# Unit tests for API integrations must mock network requests rather than hitting live endpoints. This ensures tests are fast, deterministic, and runnable offline without consuming rate limits.
# Here is an end-to-end example using Python's standard library (unittest and unittest.mock).

import unittest
from unittest.mock import Mock, patch
import requests

from user_service import UserService


class TestUserService(unittest.TestCase):

    def setUp(self):
        self.service = UserService(timeout=3)

    @patch("user_service.requests.get")
    def test_get_user_email_success(self, mock_get):
        # Configure the fake response
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.json.return_value = {
            "id": 42,
            "name": "Jane Doe",
            "email": "jane@example.com",
        }
        mock_get.return_value = fake_response

        # Execute
        email = self.service.get_user_email(42)

        # Assert output
        self.assertEqual(email, "jane@example.com")

        # Assert the endpoint was called with correct parameters
        mock_get.assert_called_once_with(
            "https://api.example.com/users/42",
            timeout=3,
        )

    @patch("user_service.requests.get")
    def test_get_user_email_404_raises_value_error(self, mock_get):
        # Configure a 404 HTTPError
        fake_response = Mock()
        fake_response.status_code = 404
        fake_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=fake_response
        )
        mock_get.return_value = fake_response

        # Verify that ValueError is raised
        with self.assertRaises(ValueError) as context:
            self.service.get_user_email(999)

        self.assertIn("User 999 not found", str(context.exception))

    @patch("user_service.requests.get")
    def test_get_user_email_timeout(self, mock_get):
        # Simulate a network timeout
        mock_get.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(ConnectionError) as context:
            self.service.get_user_email(42)

        self.assertIn("Network failure", str(context.exception))


if __name__ == "__main__":
    unittest.main()

# To run the tests, execute the following command from the project root:
# PYTHONPATH=. python -m unittest -v test_user_service.py