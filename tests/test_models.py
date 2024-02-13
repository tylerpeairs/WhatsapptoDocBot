import unittest
import uuid
import json
from unittest.mock import patch
from app.models import User, db
from app import create_app

# Mock functions for encryption and decryption removed as they're no longer needed for wa_id

class TestUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        self.session = db.session

    def tearDown(self):
        self.session.rollback()

    def test_user_creation(self):
        wa_id = str(uuid.uuid4())
        credentials_json = json.dumps({"access_token": "mock_token"})

        # Note: _serialized_credentials encryption is mocked at a higher level, not in the test directly.
        user = User(wa_id=wa_id, _serialized_credentials=credentials_json)
        self.session.add(user)
        self.session.commit()

        retrieved_user = self.session.query(User).filter_by(wa_id=wa_id).first()
        retrieved_credentials_dict = json.loads(retrieved_user._serialized_credentials)

        self.assertEqual(retrieved_user.wa_id, wa_id)
        self.assertDictEqual(retrieved_credentials_dict, json.loads(credentials_json))

    def test_unique_wa_id(self):
        wa_id = '1234567890'
        user1 = User(wa_id=wa_id, _serialized_credentials='{"access_token": "token1"}')
        self.session.add(user1)
        self.session.commit()

        user2 = User(wa_id=wa_id, _serialized_credentials='{"access_token": "token2"}')
        self.session.add(user2)
        
        # Expecting an IntegrityError due to unique constraint on wa_id
        with self.assertRaises(Exception):
            self.session.commit()

    def test_default_token_usage(self):
        wa_id = '0987654321'
        user = User(wa_id=wa_id, _serialized_credentials='{"access_token": "mock_token"}')
        self.session.add(user)
        self.session.commit()

        retrieved_user = self.session.query(User).filter_by(wa_id=wa_id).first()
        # Assuming token_usage defaults to 0 or similar logic, adjust as necessary
        self.assertEqual(retrieved_user.token_usage, None)  # Adjust based on actual default logic

if __name__ == '__main__':
    unittest.main()
