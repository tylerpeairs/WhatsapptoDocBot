import unittest
from app.models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestUser(unittest.TestCase):
    def setUp(self):
        # Set up a test database
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        self.session = Session()
        User.metadata.create_all(engine)

    def tearDown(self):
        # Clean up the test database
        self.session.rollback()
        User.metadata.drop_all(self.session.bind)

    def test_user_creation(self):
        # Create a new user
        user = User(wa_id='1234567890', serialized_credentials='{"access_token": "mock_token"}', thread_id='abc123')

        # Add the user to the session and commit the changes
        self.session.add(user)
        self.session.commit()

        # Retrieve the user from the database
        retrieved_user = self.session.query(User).filter_by(wa_id='1234567890').first()

        # Check that the retrieved user matches the original user
        self.assertEqual(retrieved_user.wa_id, '1234567890')
        self.assertEqual(retrieved_user.serialized_credentials, '{"access_token": "mock_token"}')
        self.assertEqual(retrieved_user.thread_id, 'abc123')
        self.assertEqual(retrieved_user.token_usage, 0)

    def test_unique_wa_id(self):
        # Create two users with the same WhatsApp ID
        user1 = User(wa_id='1234567890', serialized_credentials='{"access_token": "token1"}', thread_id='thread1')
        user2 = User(wa_id='1234567890', serialized_credentials='{"access_token": "token2"}', thread_id='thread2')

        # Add the users to the session and commit the changes
        self.session.add(user1)
        self.session.add(user2)
        with self.assertRaises(Exception):
            self.session.commit()

    def test_default_token_usage(self):
        # Create a new user without specifying token_usage
        user = User(wa_id='1234567890', serialized_credentials='{"access_token": "mock_token"}', thread_id='abc123')

        # Add the user to the session and commit the changes
        self.session.add(user)
        self.session.commit()

        # Retrieve the user from the database
        retrieved_user = self.session.query(User).filter_by(wa_id='1234567890').first()

        # Check that the default token_usage is 0
        self.assertEqual(retrieved_user.token_usage, 0)

if __name__ == '__main__':
    unittest.main()