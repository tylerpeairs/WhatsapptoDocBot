# Description: Utility functions for WhatsApp integration

# Import the required libraries
import logging
from flask import current_app, jsonify 
import json
import requests
import re
import datetime

# Import the database
from ..database import get_user_credentials, store_document_details, get_most_recent_document
from .google_doc_utils import create_google_docs_document, get_google_doc_content, batch_update_google_docs_document, create_update_requests
from app.utils.openai.openai_call_utils import generate_response



# Log the HTTP response
def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")

# Get the input for a text message
def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

# Send a custom text WhatsApp message
def send_message(data):
    # Set the headers
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    # Set the POST URL
    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    # Try to send the message
    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Service temporarily unavailable"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Service temporarily unavailable"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response

# Process the incoming WhatsApp message
def process_text_for_whatsapp(text):

    if not isinstance(text, str):
        raise ValueError("The input text must be a string")
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text

# Process the incoming WhatsApp message
def process_whatsapp_message(body):

    # Check timestamp to confirm it's a recent message
    time_difference_in_minutes = process_message_timestamp(body)
    # Check if the message was sent within the last minute
    if time_difference_in_minutes > 1:
        # If the message is older than 1 minutes, do not process it
        print("Message is more than a minute old, not processing.") 
        return
    else:
        # Extract the user's WhatsApp ID and name
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]


        # Check if User Exists and Get Their Credentials
        credentials = get_user_credentials(wa_id)
    


        # If user credentials do not exist, prompt the user to login
        if not credentials:
            # Use a configuration variable for the domain
            login_url = f"https://{current_app.config['APP_DOMAIN']}/login?number={wa_id}"
            response = f"For me to create and update Google Docs, I will need you to authorize me to access your Google Docs. Please do this at {login_url}"
        # If
        else:
            # Check if the user has a document
            if get_most_recent_document(wa_id) is None:
                # Create a new document
                document_details = create_google_docs_document(credentials)
                document_title = document_details['title']
                document_id = document_details['document_id']
                document_content = get_google_doc_content(credentials, document_id)
                # Store the document details in the database
                store_document_details(wa_id, document_title, document_id)
            else:
                # Get the most recent document
                document_id = get_most_recent_document(wa_id)['document_id']
                document_content = get_google_doc_content(credentials, document_id)
            
            message, categorization = generate_response(wa_id, body, document_content)
            update_request = create_update_requests(document_content, categorization, message)
            batch_update_google_docs_document(credentials, document_id, update_request)

            doc_link = f'https://docs.google.com/document/d/{document_id}/edit'
            whatsapp_response = 'Message Added: ' + message + '\nCategory: ' + categorization + '\nAccess Doc: ' + doc_link
            
            # Generate a response text message
            response = process_text_for_whatsapp(whatsapp_response)


       

    # Prepare Whatsapp JSON and send the message
    data = get_text_message_input(wa_id, response)
    send_message(data)

# Check if the incoming payload is a valid WhatsApp message
def is_valid_whatsapp_message(body):
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )


# Determine if message timestamp is greater than 5 minutes old
def process_message_timestamp(body):
    # Assuming the structure of the message body remains consistent
    message_timestamp = body['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']

    # Convert the message timestamp to a integer object
    message_timestamp = int(message_timestamp)
    
    # Convert the message timestamp to a datetime object
    message_datetime = datetime.datetime.utcfromtimestamp(message_timestamp)
    
    # Get the current datetime in UTC
    current_datetime_utc = datetime.datetime.utcnow()
    
    # Calculate the difference between the current time and the message time
    time_difference = current_datetime_utc - message_datetime
    
    # Convert time difference to minutes
    time_difference_in_minutes = time_difference.total_seconds() / 60
    
    return time_difference_in_minutes

        