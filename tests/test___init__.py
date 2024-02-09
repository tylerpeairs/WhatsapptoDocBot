import unittest
from flask import Flask
from app import create_app
from app import db

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_create_app(self):
        self.assertIsInstance(self.app, Flask)
        self.assertEqual(self.app.secret_key, 'a_secret_key')
        self.assertEqual(self.app.config['SECRET_KEY'], 'a_secret_key')

    def test_register_blueprints(self):
        # Test if blueprints are registered correctly
        # Add your assertions here
        # Test if blueprints are registered correctly
        self.assertIn('webhook', self.app.blueprints)
        self.assertIn('oauth', self.app.blueprints)
                

if __name__ == '__main__':
    unittest.main()