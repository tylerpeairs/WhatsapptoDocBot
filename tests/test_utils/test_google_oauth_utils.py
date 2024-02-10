import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.utils.google_oauth_utils import get_authorization_url, get_credentials_from_session
import json
from google.oauth2.credentials import Credentials

class TestGoogleOAuthUtils(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        # Other configuration as necessary

    def test_get_authorization_url(self):
        with self.app.test_request_context():  # Simulate a request context
            with patch('app.utils.google_oauth_utils.secrets') as mock_secrets, \
                 patch('app.utils.google_oauth_utils.session') as mock_session, \
                 patch('app.utils.google_oauth_utils.Flow') as mock_flow:

                # Mock the return values and behavior
                mock_secrets.token_urlsafe.return_value = 'mock_state'
                mock_flow.from_client_config.return_value.authorization_url.return_value = ('mock_url', 'mock_state')

                # Call the function under test
                client_config = {'web': {'redirect_uris': ['http://example.com']}}
                scopes = ['scope1', 'scope2']
                url, state = get_authorization_url(client_config, scopes)

        # Assert the results
        self.assertEqual(url, 'mock_url')
        self.assertEqual(state, 'mock_state')
        mock_session.__setitem__.assert_called_once_with('oauth_state', 'mock_state')
        mock_flow.from_client_config.assert_called_once_with(
            client_config=client_config,
            scopes=scopes,
            redirect_uri='http://example.com'
        )
        mock_flow.from_client_config.return_value.authorization_url.assert_called_once_with(
            access_type='offline',
            prompt='consent',
            state='mock_state'
        )

    @patch('google.oauth2.credentials.Credentials.from_authorized_user_info')
    def test_get_credentials_from_session(self, mock_from_authorized_user_info):
        # Create a mock Credentials object
        mock_credentials = MagicMock()

        # Mock the from_authorized_user_info to return the mock Credentials object
        mock_from_authorized_user_info.return_value = mock_credentials

        # Prepare the mock session with the mock Credentials object serialized as a JSON string
        mock_session = {'credentials': json.dumps({"dummy_key": "dummy_value"})}

        # Call the function under test
        returned_credentials = get_credentials_from_session(mock_session)

        # Assert that the returned object is the same as the mock Credentials object
        self.assertIs(returned_credentials, mock_credentials)

if __name__ == '__main__':
    unittest.main()