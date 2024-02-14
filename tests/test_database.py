import unittest
from unittest.mock import patch, MagicMock
from app.database import store_user_credentials  # Assuming generate_hash is part of database.py

class TestDatabase(unittest.TestCase):
    @patch('app.database.db.session')
    @patch('app.database.User')
    def test_store_user_credentials_existing_user(self, mock_user, mock_session):
        # Mock data
        wa_id = '1234567890'
        credentials = MagicMock()
        credentials.to_json.return_value = '{"access_token": "mock_token"}'

        # Setup a mock user to be returned by the query
        mock_user_instance = MagicMock()
        mock_user.query.filter_by.return_value.first.return_value = mock_user_instance

        # Call the function
        store_user_credentials(wa_id, credentials)

        # Verify the correct filter_by call with wa_id_hash
        mock_user.query.filter_by.assert_called_once_with(wa_id=wa_id)

        # Verify that credentials were set and session commit was called
        mock_session.commit.assert_called_once()

    @patch('app.database.db.session')
    @patch('app.database.User')
    def test_store_user_credentials_new_user(self, mock_user, mock_session):
        # Mock data
        wa_id = '1234567890'
        credentials = MagicMock(to_json=MagicMock(return_value='{"access_token": "mock_token"}'))

        # Setup the return value for querying a non-existing user
        mock_user.query.filter_by.return_value.first.return_value = None

        # Call the function
        store_user_credentials(wa_id, credentials)

        # Assertions to ensure the correct flow
        mock_user.query.filter_by.assert_called_once_with(wa_id=wa_id)
        mock_session.add.assert_called()
        mock_session.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
