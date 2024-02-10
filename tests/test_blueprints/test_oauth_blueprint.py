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


    def test_index_redirects_to_login_if_credentials_not_in_session(self):
        response = self.client.get('/')
        self.assertTrue('/login' in response.location or url_for('oauth.login', _external=True) in response.location)

    @patch('app.blueprints.oauth_blueprint.get_credentials_from_session')
    def test_index_redirects_to_login_if_not_authenticated(self, mock_get_credentials):
        # Instead of mocking valid credentials, simulate a scenario where credentials are not present or invalid
        mock_get_credentials.return_value = None

        response = self.client.get('/')

        # Assert the response redirects to the login page
        # Make sure you're using the correct path or URL for your login page
        self.assertTrue('/login' in response.headers['Location'])



    @patch('app.blueprints.oauth_blueprint.get_most_recent_document', return_value=None)
    @patch('app.blueprints.oauth_blueprint.create_google_docs_document', return_value={'document_id': '1', 'document_title': 'Test Document'})
    @patch('app.blueprints.oauth_blueprint.get_credentials_from_session')
    def test_index_creates_new_document_if_none_exists(self, mock_get_credentials_from_session, mock_create_google_docs_document, mock_get_most_recent_document):

        # Mock credentials with all necessary fields
        mock_credentials_info = {
            'client_id': 'fake-client-id',
            'client_secret': 'fake-client-secret',
            'refresh_token': 'fake-refresh-token',
            'token': 'fake-access-token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'scopes': ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'],
        }

        # Mock the get_credentials_from_session to return a Credentials object created from the mock info
        mock_credentials = MagicMock()
        mock_credentials.valid = True  # Ensure the mock Credentials object is considered valid
        # If your application checks for specific attributes or methods on the Credentials object, mock them here
        mock_get_credentials_from_session.return_value = mock_credentials_info

        with self.client.session_transaction() as sess:
            sess['credentials'] = json.dumps(mock_credentials_info)  # This line is actually not needed because you're mocking get_credentials_from_session
            sess['authenticated'] = True
            sess['wa_id'] = 'dummy_wa_id'



        response = self.client.get('/')

        print("Response status code:", response.status_code)
        mock_get_most_recent_document.assert_called_once_with('dummy_wa_id')
        print("mock_get_most_recent_document called with:", mock_get_most_recent_document.call_args)

        mock_create_google_docs_document.assert_called_once()
        print("mock_create_google_docs_document called with:", mock_create_google_docs_document.call_args)

    @patch('app.blueprints.oauth_blueprint.get_most_recent_document', return_value={'title': 'dummy_title', 'document_id': 'dummy_id'})
    @patch('app.blueprints.oauth_blueprint.create_google_docs_document', return_value={'document_id': '1', 'document_title': 'Test Document'})
    def test_index_retrieves_most_recent_document_if_exists(self, mock_create_google_docs_document, mock_get_most_recent_document):
        # Mock credentials with all necessary fields
        mock_credentials_info = {
            'client_id': 'fake-client-id',
            'client_secret': 'fake-client-secret',
            'refresh_token': 'fake-refresh-token',
            'token': 'fake-access-token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'scopes': ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'],
        }

        with self.client.session_transaction() as sess:
            sess['credentials'] = json.dumps(mock_credentials_info)  # This line is actually not needed because you're mocking get_credentials_from_session
            sess['authenticated'] = True
            sess['wa_id'] = 'dummy_wa_id'

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        mock_get_most_recent_document.assert_called()
        mock_create_google_docs_document.assert_not_called()
        
        self.assertIn("You have successfully authenticated Whatsapp to Doc Bot!", response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()