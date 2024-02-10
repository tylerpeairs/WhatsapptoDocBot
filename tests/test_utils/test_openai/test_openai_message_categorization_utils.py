import unittest
from unittest.mock import patch, MagicMock
from app.utils.openai.openai_message_categorization_utils import generate_message_and_categorization

class TestGenerateMessageAndCategorization(unittest.TestCase):

    @patch('app.utils.openai.openai_message_categorization_utils.client')
    def test_generate_message_and_categorization_success(self, mock_client):
        # Mock the response structure correctly
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text='Message: Categorized message\nCategory: Some Category')]
        mock_client.chat.completions.create.return_value = mock_response

        input_content = 'Test message'
        message, categorization = generate_message_and_categorization(input_content)

        expected_message = None
        expected_categorization = None
        self.assertEqual(message, expected_message)
        self.assertEqual(categorization, expected_categorization)

    @patch('app.utils.openai.openai_message_categorization_utils.client')
    def test_generate_message_and_categorization_retry(self, mock_client):
        # Mock the response from the OpenAI client to simulate a failure
        mock_client.chat.completions.create.side_effect = Exception('Simulated error')

        # Call the function with test input
        input_content = 'Test message'
        result = generate_message_and_categorization(input_content, max_attempts=2)

        # Assert that the function retries and returns None
        self.assertEqual(result, (None, None))

if __name__ == '__main__':
    unittest.main()