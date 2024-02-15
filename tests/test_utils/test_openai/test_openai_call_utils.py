import unittest
from unittest.mock import patch, MagicMock
from app.utils.openai.openai_call_utils import generate_response

class TestGenerateResponse(unittest.TestCase):
    @patch('app.utils.openai.openai_call_utils.generate_message_and_categorization')
    def test_generate_response_with_categories(self, mock_generate_message_and_categorization):
        body = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "text": {
                                            "body": "Hello, how are you?"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        document_content = "This is a document content"
        expected_message = "Generated message"
        expected_categorization = "Generated categorization"
        wa_id = "17777777777"

        # Set the return value of the mock
        mock_generate_message_and_categorization.return_value = (expected_message, expected_categorization)

        # Call the generate_response function
        message, categorization = generate_response(wa_id, body, document_content)

        # Assert the results
        self.assertEqual(message, expected_message)
        self.assertEqual(categorization, expected_categorization)

    @patch('app.utils.openai.openai_call_utils.generate_message_and_categorization')
    def test_generate_response_without_categories(self, mock_generate_message_and_categorization):
        body = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "text": {
                                            "body": "Hello, how are you?"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        document_content = ""
        expected_message = "Generated message"
        expected_categorization = "None"
        wa_id = "17777777777"

        # Set the return value of the mock
        mock_generate_message_and_categorization.return_value = (expected_message, expected_categorization)

        # Call the generate_response function
        message, categorization = generate_response(wa_id, body, document_content)

        # Assert the results
        self.assertEqual(message, expected_message)
        self.assertEqual(categorization, expected_categorization)

if __name__ == '__main__':
    unittest.main()
