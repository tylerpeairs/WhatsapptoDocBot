import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db

class TestExtensions(unittest.TestCase):
    def setUp(self):
        # Set up a Flask application context
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        # Clean up and remove the application context after a test
        self.ctx.pop()

    def test_db_initialized(self):
        with self.app.app_context():
            engine_url = str(db.engine.url)
            expected_url = self.app.config['SQLALCHEMY_DATABASE_URI']
            self.assertEqual(engine_url, expected_url)

if __name__ == '__main__':
    unittest.main()