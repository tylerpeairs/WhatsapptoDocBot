import unittest
import os
from unittest.mock import patch, MagicMock
from app import config

class TestConfig(unittest.TestCase):
    @patch('app.config.load_dotenv')
    def test_load_configurations(self, mock_load_dotenv):
        app = MagicMock()
        app.config = {}  # Initialize an empty dict for the config attribute


        # Set up environment variables
        os.environ["ACCESS_TOKEN"] = "mock_access_token"
        os.environ["YOUR_PHONE_NUMBER"] = "mock_phone_number"
        os.environ["APP_ID"] = "mock_app_id"
        os.environ["APP_SECRET"] = "mock_app_secret"
        os.environ["RECIPIENT_WAID"] = "mock_recipient_waid"
        os.environ["VERSION"] = "mock_version"
        os.environ["PHONE_NUMBER_ID"] = "mock_phone_number_id"
        os.environ["VERIFY_TOKEN"] = "mock_verify_token"

        config.load_configurations(app)

        # Check that the environment variables were loaded correctly
        self.assertEqual(app.config["ACCESS_TOKEN"], "mock_access_token")
        self.assertEqual(app.config["YOUR_PHONE_NUMBER"], "mock_phone_number")
        self.assertEqual(app.config["APP_ID"], "mock_app_id")
        self.assertEqual(app.config["APP_SECRET"], "mock_app_secret")
        self.assertEqual(app.config["RECIPIENT_WAID"], "mock_recipient_waid")
        self.assertEqual(app.config["VERSION"], "mock_version")
        self.assertEqual(app.config["PHONE_NUMBER_ID"], "mock_phone_number_id")
        self.assertEqual(app.config["VERIFY_TOKEN"], "mock_verify_token")

        # Check that load_dotenv was called
        mock_load_dotenv.assert_called_once()

if __name__ == '__main__':
    unittest.main()