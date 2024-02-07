# Description: OpenAI API call utilities

# Import the required libraries
import logging
import json 
from ..google_doc_utils import parse_existing_categories
from .openai_message_categorization_utils import generate_message_and_categorization


# Generate a response from the chat completions
def generate_response(body, document_content):
    # Extract the message body
    message_body = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
    message_body = body 
    logging.info(f"Message Body: {message_body}")

    # Extract the categories from the document content
    doc_categories_indexed, _ = parse_existing_categories(document_content)
    doc_categories = doc_categories_indexed.keys()
    logging.info(f"Document Categories: {doc_categories}")

    # Generate a user message
    message_and_categorization_input_content = {
        "whatsapp_text_message": message_body,
        "categories": doc_categories
    }
    logging.info(f"Message and Categorization Input Content: {message_and_categorization_input_content}")

    # Generate a readable message with a category
    string_message_and_categorization_input_content = json.dumps(message_and_categorization_input_content)
    message, categorization = generate_message_and_categorization(string_message_and_categorization_input_content)
    

    return message, categorization


# To-do
# Generate and test the generate_json_prompt with output test cases use function calling tool for responses format response_format={ "type": "json_object" }
# Build generate_json_prompt function
# Add Output Validators & Try/Catch for json_request (Could even use an output validation model)
# Call json_request with batch_update_google_docs_document function
# Format whatsapp message according to outputs
# Token Storage
