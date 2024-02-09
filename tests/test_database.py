import unittest
from unittest.mock import patch, MagicMock
from app.database import store_user_credentials
from app.models import User

class TestDatabase(unittest.TestCase):
    @patch('app.database.User.query')
    @patch('app.database.db.session')
    def test_store_user_credentials_existing_user(self, mock_session, mock_query):
        # Mock data
        wa_id = '1234567890'
        credentials = MagicMock()
        user = MagicMock()

        # Mock function return values
        mock_query.filter_by.return_value.first.return_value = user

        # Call the function
        store_user_credentials(wa_id, credentials)

        # Assert that the query was called with the correct arguments
        mock_query.filter_by.assert_called_once_with(wa_id=wa_id)
        mock_query.filter_by.return_value.first.assert_called_once()

        # Assert that the user's credentials were updated
        user.serialized_credentials = credentials.to_json.assert_called_once()

        # Assert that the session was committed
        mock_session.commit.assert_called_once()

    @patch('app.database.User.query')
    @patch('app.database.db.session')
    def test_store_user_credentials_new_user(self, mock_session, mock_query):
        # Mock data
        wa_id = '1234567890'
        credentials = MagicMock()

        # Mock function return values
        mock_query.filter_by.return_value.first.return_value = None

        # Call the function
        store_user_credentials(wa_id, credentials)

        # Assert that the query was called with the correct arguments
        mock_query.filter_by.assert_called_once_with(wa_id=wa_id)
        mock_query.filter_by.return_value.first.assert_called_once()

        # Assert that a new user was created
        mock_session.add.assert_called()

        # Assert that the session was committed
        mock_session.commit.assert_called_once()