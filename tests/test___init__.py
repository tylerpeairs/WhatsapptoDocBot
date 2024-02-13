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

    def test_register_blueprints(self):
        self.assertIn('webhook', self.app.blueprints)
        self.assertIn('oauth', self.app.blueprints)
                

if __name__ == '__main__':
    unittest.main()