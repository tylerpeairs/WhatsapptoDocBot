import unittest
from unittest.mock import patch, MagicMock, ANY
from flask import url_for
from flask_testing import TestCase
from app import create_app
import json

class TestIndex(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app

    @patch('app.blueprints.oauth_blueprint.get_user_credentials')
    def test_index_redirects_to_login_if_not_authenticated(self, mock_get_user_credentials):
        # Instead of mocking valid credentials, simulate a scenario where credentials are not present or invalid
        mock_get_user_credentials.return_value = None

        response = self.client.get('/')

        # Assert the response redirects to the login page
        # Make sure you're using the correct path or URL for your login page
        self.assertTrue('/login' in response.headers['Location'])


    @patch('app.blueprints.oauth_blueprint.get_user_credentials')
    @patch('app.blueprints.oauth_blueprint.get_most_recent_document', return_value=None)
    @patch('app.blueprints.oauth_blueprint.create_google_docs_document', return_value={'document_id': '1', 'document_title': 'Test Document'})
    def test_index_creates_new_document_if_none_exists(self, mock_get_user_credentials, mock_create_google_docs_document, mock_get_most_recent_document):

        # Mock credentials with all necessary fields
        mock_credentials_info = {
            'client_id': 'fake-client-id',
            'client_secret': 'fake-client-secret',
            'refresh_token': 'fake-refresh-token',
            'token': 'fake-access-token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'scopes': ['https://www.googleapis.com/auth/documents'],
        }

        # Mock the get_credentials_from_session to return a Credentials object created from the mock info
        mock_credentials = MagicMock()
        mock_credentials.valid = True  # Ensure the mock Credentials object is considered valid
        # If your application checks for specific attributes or methods on the Credentials object, mock them here
        mock_get_user_credentials.return_value = mock_credentials_info

        with self.client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['wa_id'] = 'dummy_wa_id'
        response = self.client.get('/')

        print("Response status code:", response.status_code)
        mock_get_most_recent_document.assert_called_with('dummy_wa_id')
        print("mock_get_most_recent_document called with:", mock_get_most_recent_document.call_args)

        mock_create_google_docs_document.assert_called_once()
        print("mock_create_google_docs_document called with:", mock_create_google_docs_document.call_args)
    
    @patch('app.blueprints.oauth_blueprint.get_user_credentials')
    @patch('app.blueprints.oauth_blueprint.get_most_recent_document', return_value={'title': 'dummy_title', 'document_id': 'dummy_id'})
    @patch('app.blueprints.oauth_blueprint.create_google_docs_document', return_value={'document_id': '1', 'document_title': 'Test Document'})
    def test_index_retrieves_most_recent_document_if_exists(self, mock_get_user_credentials, mock_create_google_docs_document, mock_get_most_recent_document):
        # Mock credentials with all necessary fields
        mock_credentials_info = {
            'client_id': 'fake-client-id',
            'client_secret': 'fake-client-secret',
            'refresh_token': 'fake-refresh-token',
            'token': 'fake-access-token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'scopes': ['https://www.googleapis.com/auth/documents'],
        }

        with self.client.session_transaction() as sess:
            sess['authenticated'] = True
            sess['wa_id'] = 'dummy_wa_id'

        mock_get_user_credentials.return_value = mock_credentials_info
        mock_get_most_recent_document.return_value = {'title': 'dummy_title', 'document_id': 'dummy_id'}

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        mock_get_most_recent_document.assert_called()
        self.assertIn("You have successfully authenticated Whatsapp to Doc Bot!", response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()