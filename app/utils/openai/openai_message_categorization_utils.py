# This module contains the utility functions for generating a message and categorization from chat completions  

# Import the required libraries
import os
import time
import logging
import re
from dotenv import load_dotenv
from openai import OpenAI
from ...database import update_token_usage

# Load the environment variables
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

system_content = '''
You are an expert at making whatsapp text messages more readable and categorizing them. A user will provide inputs and you will follow the instructions step-by-step and obey the rules.

# Inputs
whatsapp_text_message: {{whatsapp_text_message}}
categories: {{categories}}

# Instructions
1. You will go through the categories array and select the most relevant category for the whatsapp_text_message. If there isn't an extremely relevant and topical category, generate a new, relevant category.
2. Using the selected or generated category, rewrite the whatsapp_text_message to improve readability and specificity.
3. Provide the rewritten message and category in the output format.

# Rules
1. You will always choose or generate a category.
2. Always format the category and message into the output format.
3. Don't rewrite the message if it changes the meaning. Just correct punctuation, spelling, and grammar in such cases.
4. If there are no categories, generate one.
5. If the chosen category does not seem extremely relevant, generate a new category.

# Examples
Example 1 Input:
whatsapp_text_message: "Got 300 pesos Tyler"
categories: ""
Example 1 Output:
Message: Received 300 pesos from Tyler.
Category: Money Received

Example 2 Input:
whatsapp_text_message: "Got 300 pesos Tyler"
categories: "Personal, Legal"
Example 2 Output:
Message: Received 300 pesos from Tyler.
Category: Money Received

Example 3 Input:
whatsapp_text_message: "Finished testing functions in program"
categories: "Personal, Legal, Money Received, Real Estate"
Example 3 Output:
Message: "Finished testing functions in program."
Category: Computer Programdg

# Output Format
Message: 
Category: 
'''

# Function to generate a message and categorization from chat completions
def generate_message_and_categorization(wa_id, message_and_categorization_input_content, max_attempts = 2):
    messages = [
        {
        "role": "system",
        "content": system_content
        },
        {
        "role": "user",
        "content": message_and_categorization_input_content
        }
    ]
    attempts = 0
    token_count = 0
    while attempts <= max_attempts:
        logging.info(f"Attempt: {attempts}")
        try:
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=messages,
                temperature=0.5,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            validated_response = validate_and_parse_messaging_categorization(response)
            logging.info(f"Response: {response}")
            token_count += response.usage.total_tokens
            logging.info(f"Validated Response: {validated_response}")
            if validated_response[0] == True:
                logging.info(f"Token Count: {token_count}")
                update_token_usage(wa_id, token_count)
                return validated_response[1], validated_response[2]
            else:
                attempts += 1
                time.sleep(5)
                continue
        except Exception as e:
            logging.error(f"Error: {e}")
            attempts += 1
            time.sleep(5)

    return None, None

# Function to validate and parse the messaging categorization
def validate_and_parse_messaging_categorization(response):
    response_message = response.choices[0].message.content
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

