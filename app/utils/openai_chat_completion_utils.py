from email import message
from re import M
from openai import OpenAI
from dotenv import load_dotenv
import logging
import os
import time
import json
import re
from regex import F

from sqlalchemy import true
from app.database import store_thread, get_most_recent_document, get_user_credentials, check_if_thread_exists, update_token_usage
from .google_doc_utils import batch_update_google_docs_document

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

test_flag = True

# Function to extract HEADING_1 paragraph texts
def extract_heading_1_text(doc_json):
    heading_texts = []  # Initialize an empty list to store heading texts
    for content_item in doc_json["content"]:
        if "paragraph" in content_item:  # Check if the content item is a paragraph
            paragraph = content_item["paragraph"]
            if paragraph.get("paragraphStyle", {}).get("namedStyleType") == "HEADING_1":
                for element in paragraph["elements"]:
                    text = element["textRun"]["content"].replace("\n", "")  # Remove newlines
                    heading_texts.append(text)
    return heading_texts

# Generate a response from the chat completions
def generate_response(body, document_content):
    # Extract the message body
    if test_flag == False:
        message_body = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
    else:
        message_body = body 
    logging.info(f"Message Body: {message_body}")

    # Extract the categories from the document content
    doc_categories = extract_heading_1_text(document_content)
    logging.info(f"Document Categories: {doc_categories}")

    # Generate a user message
    message_and_categorization_input_content = {
        "whatsapp_text_message": message_body,
        "categories": doc_categories
    }
    logging.info(f"Message and Categorization Input Content: {message_and_categorization_input_content}")

    # Generate a readable message with a category
    if test_flag == False:
        string_message_and_categorization_input_content = json.dumps(message_and_categorization_input_content)
        response = generate_message_and_categorization(string_message_and_categorization_input_content)
        logging.info(f"Response: {response}")
        whatsapp_response = response["choices"][0]["message"]["content"]
    else:
        whatsapp_response = "Dummy Response"


    return whatsapp_response

# Function to generate a message and categorization from chat completions
def generate_message_and_categorization(message_and_categorization_input_content, max_attempts = 2):
    attempts = 0
    while attempts <= max_attempts:
        try:
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {
                    "role": "system",
                    "content": "You are an expert at making whatsapp text messages more readable and categorizing them. A user will provide inputs and you will follow the instructions and rules.\n\n# Inputs\nwhatsapp_text_message: {{whatsapp_text_message}}\ncategories: {{categories}}\n\n# Instructions\n1. You will go through the category array and select the most relevant category for the whatsapp_text_message. If there isn't a highly relevant category, generate a relevant category.\n2. Using the selected or generated category, rewrite the whatsapp_text_message to improve readability and specificity.\n3. Provide the rewritten message and category in the output format.\n\n# Rules\n1. You will always choose or generate a category.\n2. Always format the category and message into the output format.\n\n# Output Format\nMessage: \nCategory: "
                    },
                    {
                    "role": "user",
                    "content": message_and_categorization_input_content
                    }
                ],
                temperature=0.5,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            validated_response = validate_and_parse_messaging_categorization(response)
            if validated_response[0] == True:
                return response
            else:
                attempts += 1
                time.sleep(5)
                continue
        except Exception as e:
            logging.error(f"Error: {e}")
            attempts += 1
            time.sleep(5)


# Function to validate and parse the messaging categorization
def validate_and_parse_messaging_categorization(response):
    if test_flag == False:
        response_message = response["choices"][0]["message"]["content"]
    else:
        response_message = response

    # Define the pattern for the expected format 
    pattern = r'^Message: (.+)\nCategory: (.+)$'

    # Use re.match to check if the message_body matches the pattern
    match = re.match(pattern, response_message)
    
    if match:
        # If there's a match, extract the message and category parts
        message_text = match.group(1)
        category_text = match.group(2)
        return True, message_text, category_text
    else:
        # If there's no match, the format is not as expected
        return False, None, None

# To-do
# Build parser for output of generate_message_and_categorization
# Generate and test the generate_json_prompt with output test cases
# Build generate_json_prompt function
# Call json_request with batch_update_google_docs_document function
# Add Output Validators & Try/Catch for openapi calls
# Format whatsapp message according to outputs
# Token Storage


#==========================
#Test
#==========================
if test_flag == True:
    # Test Inputs for Message Categorizer
    '''
    google_docs_json_example_1 = {

        "content": [
        {
            "endIndex": 1,
            "sectionBreak": {
            "sectionStyle": {
                "columnSeparatorStyle": "NONE",
                "contentDirection": "LEFT_TO_RIGHT",
                "sectionType": "CONTINUOUS"
            }
            }
        },
        {
            "startIndex": 1,
            "endIndex": 16,
            "paragraph": {
            "elements": [
                {
                "startIndex": 1,
                "endIndex": 16,
                "textRun": {
                    "content": "Money Received\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "headingId": "h.e1m8oigbc93",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 16,
            "endIndex": 46,
            "paragraph": {
            "elements": [
                {
                "startIndex": 16,
                "endIndex": 46,
                "textRun": {
                    "content": "Received 300 pesos from Tyler\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 46,
            "endIndex": 52,
            "paragraph": {
            "elements": [
                {
                "startIndex": 46,
                "endIndex": 52,
                "textRun": {
                    "content": "Legal\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "headingId": "h.yi6mteyiqxog",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 52,
            "endIndex": 68,
            "paragraph": {
            "elements": [
                {
                "startIndex": 52,
                "endIndex": 68,
                "textRun": {
                    "content": "Permit Problems\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 68,
            "endIndex": 78,
            "paragraph": {
            "elements": [
                {
                "startIndex": 68,
                "endIndex": 78,
                "textRun": {
                    "content": "Prospects\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "headingId": "h.dpp1e43gbzqq",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 78,
            "endIndex": 108,
            "paragraph": {
            "elements": [
                {
                "startIndex": 78,
                "endIndex": 108,
                "textRun": {
                    "content": "Tyler wants to see Ventanilla\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        }
        ]
    }
    google_docs_json_example_2 = {
        "content": [
        {
            "endIndex": 1,
            "sectionBreak": {
            "sectionStyle": {
                "columnSeparatorStyle": "NONE",
                "contentDirection": "LEFT_TO_RIGHT",
                "sectionType": "CONTINUOUS"
            }
            }
        },
        {
            "startIndex": 1,
            "endIndex": 16,
            "paragraph": {
            "elements": [
                {
                "startIndex": 1,
                "endIndex": 16,
                "textRun": {
                    "content": "Money Received\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "headingId": "h.e1m8oigbc93",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 16,
            "endIndex": 46,
            "paragraph": {
            "elements": [
                {
                "startIndex": 16,
                "endIndex": 46,
                "textRun": {
                    "content": "Received 300 pesos from Tyler\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 46,
            "endIndex": 52,
            "paragraph": {
            "elements": [
                {
                "startIndex": 46,
                "endIndex": 52,
                "textRun": {
                    "content": "Legal\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "headingId": "h.yi6mteyiqxog",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 52,
            "endIndex": 68,
            "paragraph": {
            "elements": [
                {
                "startIndex": 52,
                "endIndex": 68,
                "textRun": {
                    "content": "Permit Problems\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 68,
            "endIndex": 78,
            "paragraph": {
            "elements": [
                {
                "startIndex": 68,
                "endIndex": 78,
                "textRun": {
                    "content": "Prospects\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "headingId": "h.dpp1e43gbzqq",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 78,
            "endIndex": 108,
            "paragraph": {
            "elements": [
                {
                "startIndex": 78,
                "endIndex": 108,
                "textRun": {
                    "content": "Tyler wants to see Ventanilla\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 108,
            "endIndex": 138,
            "paragraph": {
            "elements": [
                {
                "startIndex": 108,
                "endIndex": 138,
                "textRun": {
                    "content": "Tyler wants to see Ventanilla\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 138,
            "endIndex": 149,
            "paragraph": {
            "elements": [
                {
                "startIndex": 138,
                "endIndex": 149,
                "textRun": {
                    "content": "Money Owed\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "headingId": "h.wct4dpsxjrpd",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 149,
            "endIndex": 155,
            "paragraph": {
            "elements": [
                {
                "startIndex": 149,
                "endIndex": 155,
                "textRun": {
                    "content": "To-Do\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "headingId": "h.x9s19picaxz8",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 155,
            "endIndex": 156,
            "paragraph": {
            "elements": [
                {
                "startIndex": 155,
                "endIndex": 156,
                "textRun": {
                    "content": "\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 156,
            "endIndex": 157,
            "paragraph": {
            "elements": [
                {
                "startIndex": 156,
                "endIndex": 157,
                "textRun": {
                    "content": "\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        },
        {
            "startIndex": 157,
            "endIndex": 158,
            "paragraph": {
            "elements": [
                {
                "startIndex": 157,
                "endIndex": 158,
                "textRun": {
                    "content": "\n",
                    "textStyle": {}
                }
                }
            ],
            "paragraphStyle": {
                "namedStyleType": "NORMAL_TEXT",
                "direction": "LEFT_TO_RIGHT"
            }
            }
        }
        ]
    }
    message_body_1 = "Got 300 pesos Tyler"
    message_body_2 = "Permit problems Ventanilla"
    test_output_1 = generate_response(message_body_1, google_docs_json_example_1)
    test_output_2 = generate_response(message_body_2, google_docs_json_example_2)
    '''

    #Test Inputs for Message Validator and Parser
    response_message_1 = 'Message: Tyler received 300 pesos.\nCategory: Money Received'
    response_message_2 = 'Message: We are currently experiencing issues with obtaining permits at Ventanilla.\nCategory: Legal'
    output_1 = validate_and_parse_messaging_categorization(response_message_1)
    output_2 = validate_and_parse_messaging_categorization(response_message_2)
    logging.info(f"Output 1: {output_1}")
    logging.info(f"Output 2: {output_2}")
