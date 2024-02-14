import unittest
import uuid
import json
from app.models import User, db
from app import create_app

# Assuming TestConfig is meant for isolated test DB configuration
class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use an in-memory database for truly isolated tests
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional: Disable track modifications to suppress warning and slightly improve performance

class TestUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestConfig)  # Assuming create_app can accept a config object
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Instead of dropping all tables, just remove the session
        db.session.remove()
        cls.app_context.pop()

    def setUp(self):
        self.session = db.session

    def tearDown(self):
        # Rollback the session to undo transactions
        self.session.rollback()
        # Clear data from each table
        for table in reversed(db.metadata.sorted_tables):
            self.session.execute(table.delete())
        self.session.commit()

    def test_user_creation(self):
        wa_id = str(uuid.uuid4())
        credentials_json = json.dumps({"access_token": "mock_token"})

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
        
        with self.assertRaises(Exception):
            self.session.commit()

    def test_default_token_usage(self):
        wa_id = '0987654321'
        user = User(wa_id=wa_id, _serialized_credentials='{"access_token": "mock_token"}')
        self.session.add(user)
        self.session.commit()

        retrieved_user = self.session.query(User).filter_by(wa_id=wa_id).first()
        self.assertEqual(retrieved_user.token_usage, None)  # Adjust based on actual default logic

if __name__ == '__main__':
    unittest.main()
