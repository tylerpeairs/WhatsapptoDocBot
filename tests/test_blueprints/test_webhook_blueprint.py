import unittest
from flask import Flask, jsonify
from flask.testing import FlaskClient
from unittest.mock import patch
from app.blueprints.webhook_blueprint import handle_message
import json

class TestHandleMessage(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        super().setUp()
        # Temporary route for testing
        @self.app.route('/webhook', methods=['POST'])
        def test_webhook():
            return handle_message()

    def test_handle_message_valid_whatsapp_message(self):
        valid_whatsapp_message_payload = {
            "object": "whatsapp",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                    "text": "Test message",
                                    "timestamp": 1234567890
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        with self.app.test_request_context(method='POST', data=json.dumps(valid_whatsapp_message_payload), content_type='application/json'):
            response, status_code = handle_message()
            self.assertEqual(status_code, 200)
            self.assertEqual(response.get_json(), {'status': 'ok'})
                # Add additional assertions for the expected behavior when handling a valid WhatsApp message

    def test_handle_message_whatsapp_status_update(self):
        with self.app.test_request_context(json={
        "object": "some_object",
        "entry": [
            {
            "changes": [
                {
                "value": {
                    "messages": [
                    {
                        "some_key": "some_value",
                    }
                    ],
                    "statuses": True,
                }
                }
            ]
            }
        ]
        }):
            response, status_code = handle_message()
            self.assertEqual(status_code, 200)
            self.assertEqual(response.get_json(), {'status': 'ok'})

            # Add additional assertions for the expected behavior when handling a WhatsApp status update

    def test_handle_message_invalid_whatsapp_event(self):
        with self.app.test_request_context(json={'event': 'invalid_event'}):
            response, status_code = handle_message()
            self.assertEqual(status_code, 404)
            self.assertEqual(response.get_json(), {'status': 'error', 'message': 'Not a WhatsApp API event'})

            # Add additional assertions for the expected behavior when handling an invalid WhatsApp event

    def test_handle_message_invalid_json(self):
        response = self.client.post(
            '/webhook',  # Confirm this endpoint is correctly set up to handle POST requests
            data='{"invalid": "json"',  # Malformed JSON
            content_type='application/json'
        )
        print("response: ", response.data)
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()