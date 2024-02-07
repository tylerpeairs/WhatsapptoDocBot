# This module contains the utility functions for generating a message and categorization from chat completions  

# Import the required libraries
import os
import time
import logging
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load the environment variables
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

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
                return validated_response[1], validated_response[2]
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

