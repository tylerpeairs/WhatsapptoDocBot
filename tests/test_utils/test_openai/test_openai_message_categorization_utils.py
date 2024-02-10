import unittest
from unittest.mock import patch, MagicMock
from app.utils.openai.openai_message_categorization_utils import generate_message_and_categorization

class TestGenerateMessageAndCategorization(unittest.TestCase):

    @patch('app.utils.openai.openai_message_categorization_utils.client')
    @patch('app.utils.openai.openai_message_categorization_utils.validate_and_parse_messaging_categorization')
    @patch('app.utils.openai.openai_message_categorization_utils.update_token_usage')
    def test_generate_message_and_categorization_success(self, mock_update_token_usage, mock_validate, mock_client):
        # Mock the response structure correctly
        mock_response = MagicMock()
        
        # Mock the validate_and_parse_messaging_categorization to return True, and desired message and category
        mock_validate.return_value = (True, 'Categorized message', 'Some Category')

        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=40, total_tokens=50)
        mock_response.choices = [MagicMock(text='Message: Categorized message\nCategory: Some Category')]
        mock_client.chat.completions.create.return_value = mock_response
        wa_id = "17777777777"

        input_content = 'Test message'
        message, categorization = generate_message_and_categorization(wa_id, input_content)


        # Check if update_token_usage was called correctly
        mock_update_token_usage.assert_called_once_with(wa_id, 50)

        expected_message = 'Categorized message'
        expected_categorization = 'Some Category'
        self.assertEqual(message, expected_message)
        self.assertEqual(categorization, expected_categorization)



    @patch('app.utils.openai.openai_message_categorization_utils.update_token_usage')
    @patch('app.utils.openai.openai_message_categorization_utils.client')
    def test_generate_message_and_categorization_retry(self, mock_client, mock_update_token_usage):
        # Mock the response from the OpenAI client to simulate a failure
        mock_client.chat.completions.create.side_effect = Exception('Simulated error')
        wa_id = "17777777777"

        # Call the function with test input
        input_content = 'Test message'
        result = generate_message_and_categorization(wa_id, input_content, max_attempts=2)

        # Assert that the function retries and returns None
        self.assertEqual(result, (None, None))

        # Check that update_token_usage was not called due to failure
        mock_update_token_usage.assert_not_called()


if __name__ == '__main__':
    unittest.main()