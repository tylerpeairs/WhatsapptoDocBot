import unittest
from unittest.mock import patch, MagicMock, call
import requests
from flask import Flask
from app.utils.whatsapp_utils import (
    log_http_response,
    get_text_message_input,
    send_message,
    process_text_for_whatsapp,
    process_whatsapp_message,
    is_valid_whatsapp_message,
    process_message_timestamp,
)


class TestWhatsAppUtils(unittest.TestCase):
    def setUp(self):
        # Set up a Flask application context
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['ACCESS_TOKEN'] = 'mock_access_token'
        self.app.config['VERSION'] = 'mock_version'
        self.app.config['PHONE_NUMBER_ID'] = 'mock_phone_number_id'
        self.ctx = self.app.app_context()
        self.ctx.push()  # This line was missing

    def tearDown(self):
        # Clean up and remove the application context after a test
        self.ctx.pop()
    
    @patch('logging.info')
    def test_log_http_response(self, mock_logging_info):
        response = MagicMock()
        response.status_code = 200
        response.headers.get.return_value = 'application/json'
        response.text = '{"message": "Success"}'


        log_http_response(response)

        # Check that all expected log messages were made
        expected_calls = [
            call('Status: 200'),
            call('Content-type: application/json'),
            call('Body: {"message": "Success"}')
        ]
        mock_logging_info.assert_has_calls(expected_calls, any_order=True)

    def test_get_text_message_input(self):
        recipient = '1234567890'
        text = 'Hello, world!'

        expected_output = (
            '{"messaging_product": "whatsapp", "recipient_type": "individual", "to": "1234567890", '
            '"type": "text", "text": {"preview_url": false, "body": "Hello, world!"}}'
        )

        output = get_text_message_input(recipient, text)

        self.assertEqual(output, expected_output)

    @patch('requests.post')
    def test_send_message_success(self, mock_requests_post):
        data = '{"message": "Hello"}'
        response = MagicMock()
        response.status_code = 200

        mock_requests_post.return_value = response

        output = send_message(data)

        mock_requests_post.assert_called_with(
            f"https://graph.facebook.com/{self.app.config['VERSION']}/{self.app.config['PHONE_NUMBER_ID']}/messages",
            data='{"message": "Hello"}',
            headers={
                'Content-type': 'application/json',
                'Authorization': f"Bearer {self.app.config['ACCESS_TOKEN']}"
            },
            timeout=10
        )
        response.raise_for_status.assert_called()
        self.assertEqual(output, response)

    @patch('requests.post')
    def test_send_message_timeout(self, mock_requests_post):
        data = '{"message": "Hello"}'

        mock_requests_post.side_effect = requests.Timeout

        output, status_code = send_message(data)

        mock_requests_post.assert_called_with(
            f"https://graph.facebook.com/{self.app.config['VERSION']}/{self.app.config['PHONE_NUMBER_ID']}/messages",
            data='{"message": "Hello"}',
            headers={
                'Content-type': 'application/json',
                'Authorization': f"Bearer {self.app.config['ACCESS_TOKEN']}"
            },
            timeout=10
        )
        
        # Validate the status code
        self.assertEqual(status_code, 408)

        json_data = output.get_json()
        self.assertEqual(json_data, {"status": "error", "message": "Request timed out"})


    @patch('requests.post')
    def test_send_message_request_exception(self, mock_requests_post):
        data = '{"message": "Hello"}'
        mock_requests_post.side_effect = requests.RequestException

        output, status_code = send_message(data)

        json_data = output.get_json()

        mock_requests_post.assert_called_with(
            f"https://graph.facebook.com/{self.app.config['VERSION']}/{self.app.config['PHONE_NUMBER_ID']}/messages",
            data='{"message": "Hello"}',
            headers={
                'Content-type': 'application/json',
                'Authorization': f"Bearer {self.app.config['ACCESS_TOKEN']}"
            },
            timeout=10
        )
        
        # Validate the status code
        self.assertEqual(status_code, 500)

        json_data = output.get_json()
        self.assertEqual(json_data, {"status": "error", "message": "Failed to send message"})

    def test_process_text_for_whatsapp(self):
        text = 'Hello **world**! This is a **test** message.'

        expected_output = 'Hello *world*! This is a *test* message.'

        output = process_text_for_whatsapp(text)

        self.assertEqual(output, expected_output)

    def test_is_valid_whatsapp_message(self):
        body = {
            "object": "page",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "text": "Hello",
                                        "timestamp": "1631234567"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        output = is_valid_whatsapp_message(body)

        self.assertTrue(output)

    def test_process_message_timestamp(self):
        body = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "timestamp": "1631234567"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        output = process_message_timestamp(body)

        self.assertGreater(output, 1)

class TestProcessWhatsAppMessage(unittest.TestCase):

    def setUp(self):
        # Set up a Flask application context
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['ACCESS_TOKEN'] = 'mock_access_token'
        self.app.config['VERSION'] = 'mock_version'
        self.app.config['PHONE_NUMBER_ID'] = 'mock_phone_number_id'
        self.app.config['RECIPIENT_WAID'] = 'mock_recipient_id'
        self.ctx = self.app.app_context()
        self.ctx.push()  # This line was missing

    def tearDown(self):
        # Clean up and remove the application context after a test
        self.ctx.pop()
    

    @patch('app.utils.whatsapp_utils.process_message_timestamp')
    @patch('app.utils.whatsapp_utils.get_user_credentials')
    @patch('app.utils.whatsapp_utils.get_most_recent_document')
    @patch('app.utils.whatsapp_utils.create_google_docs_document')
    @patch('app.utils.whatsapp_utils.get_google_doc_content')
    @patch('app.utils.whatsapp_utils.store_document_details')
    @patch('app.utils.whatsapp_utils.generate_response')
    @patch('app.utils.whatsapp_utils.create_update_requests')
    @patch('app.utils.whatsapp_utils.batch_update_google_docs_document')
    @patch('app.utils.whatsapp_utils.process_text_for_whatsapp')
    @patch('app.utils.whatsapp_utils.get_text_message_input')
    @patch('app.utils.whatsapp_utils.send_message')
    def test_process_whatsapp_message(self, mock_send_message, mock_get_text_message_input, mock_process_text_for_whatsapp,
                                      mock_batch_update_google_docs_document, mock_create_update_requests,
                                      mock_generate_response, mock_store_document_details, mock_get_google_doc_content,
                                      mock_create_google_docs_document, mock_get_most_recent_document,
                                      mock_get_user_credentials, mock_process_message_timestamp):
        # Mock data
        body = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "contacts": [
                                    {
                                        "wa_id": "1234567890"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        credentials = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token"
        }
        document_details = {
            "title": "Mock Document",
            "document_id": "mock_document_id"
        }
        document_content = "Mock Document Content"
        message = "Mock Message"
        categorization = "Mock Categorization"
        update_request = "Mock Update Request"
        response = f"Message Added: {message}\nCategory: {categorization}\nAccess Doc: https://docs.google.com/document/d/mock_document_id/edit"
        text_message_input = "Mock Text Message Input"

        # Mock function return values
        mock_process_message_timestamp.return_value = 0
        mock_get_user_credentials.return_value = credentials
        mock_get_most_recent_document.return_value = None
        mock_create_google_docs_document.return_value = document_details
        mock_get_google_doc_content.return_value = document_content
        mock_generate_response.return_value = (message, categorization)
        mock_create_update_requests.return_value = update_request
        mock_process_text_for_whatsapp.return_value = response
        mock_get_text_message_input.return_value = text_message_input

        # Call the function
        process_whatsapp_message(body)

        # Assert the function calls
        mock_process_message_timestamp.assert_called_once_with(body)
        mock_get_user_credentials.assert_called_once_with("1234567890")
        mock_get_most_recent_document.assert_called_once_with("1234567890")
        mock_create_google_docs_document.assert_called_once_with(credentials)
        mock_get_google_doc_content.assert_called_once_with(credentials, "mock_document_id")
        mock_store_document_details.assert_called_once_with("1234567890", "Mock Document", "mock_document_id")
        mock_generate_response.assert_called_once_with(body, document_content)
        mock_create_update_requests.assert_called_once_with(document_content, categorization, message)
        mock_batch_update_google_docs_document.assert_called_once_with(credentials, "mock_document_id", update_request)
        mock_process_text_for_whatsapp.assert_called_once_with(response)
        mock_get_text_message_input.assert_called_once_with(self.app.config['RECIPIENT_WAID'], response)
        mock_send_message.assert_called_once_with(text_message_input)

if __name__ == '__main__':
    unittest.main()