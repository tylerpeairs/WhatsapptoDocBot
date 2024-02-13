# Description: OpenAI API call utilities

# Import the required libraries
from ..google_doc_utils import parse_existing_categories
from .openai_message_categorization_utils import generate_message_and_categorization

# Generate a response from the chat completions
def generate_response(wa_id, body, document_content):
    # Extract the message body
    message_body = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

    # Extract the categories from the document content
    doc_categories_indexed = parse_existing_categories(document_content)
    doc_categories = list(doc_categories_indexed.keys())

    # Generate a readable message with a category
    string_message_and_categorization_input_content = f"whatsapp_text_message: {message_body}\ncategories: {'None' if not doc_categories else ', '.join(doc_categories)}"
    message, categorization = generate_message_and_categorization(wa_id, string_message_and_categorization_input_content)
    

    return message, categorization
