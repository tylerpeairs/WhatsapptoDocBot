from flask import Flask, jsonify
import unittest
from unittest.mock import patch
from functools import wraps
from app.decorators.security import signature_required 

# Assuming your decorator and validate_signature function are correctly defined as shown previously

def create_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["APP_SECRET"] = "test_secret"

    @app.route('/test', methods=['POST'])
    @signature_required
    def test_route():
        return jsonify({"status": "success"}), 200

    return app

class TestSignatureRequiredDecorator(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    @patch('app.decorators.security.validate_signature')
    def test_signature_required_valid_signature(self, mock_validate_signature):
        mock_validate_signature.return_value = True

        response = self.client.post('/test', headers={"X-Hub-Signature-256": "sha256=valid_signature"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "success"})

    @patch('app.decorators.security.validate_signature')
    def test_signature_required_invalid_signature(self, mock_validate_signature):
        mock_validate_signature.return_value = False

        response = self.client.post('/test', headers={"X-Hub-Signature-256": "sha256=invalid_signature"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json, {"status": "error", "message": "Invalid signature"})

if __name__ == '__main__':
    unittest.main()
