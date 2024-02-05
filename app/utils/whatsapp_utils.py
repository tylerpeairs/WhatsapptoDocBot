# Description: Utility functions for WhatsApp integration

# Import the required libraries
from functools import update_wrapper
import logging
from flask import current_app, jsonify, session
import json
import requests
import re

# Import the database
from ..models import User, Document
from ..database import get_user_credentials, store_document_details, get_most_recent_document
from .google_doc_utils import create_google_docs_document, get_google_doc, batch_update_google_docs_document
from google.oauth2.credentials import Credentials
from .openai_assistant_utils import generate_response

# Update Whatsapp Utils for any credentials related references
# Update Prompt to pass in credentials object instead


# Import the OpenAI service
#from app.services.openai_service import generate_response


# Log the HTTP response
def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")

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
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response

# Process the incoming WhatsApp message
def process_text_for_whatsapp(text):
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
    logging.info(f"Received WhatsApp message body: {body}")

    # Extract the user's WhatsApp ID and name
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]


    # Check if User Exists and Get Their Credentials
    credentials = get_user_credentials(wa_id)
    logging.info(f"credentials: {credentials}")


    # If user credentials do not exist, prompt the user to login
    if not credentials:
        login_url = f"https://deciding-werewolf-infinitely.ngrok-free.app/login?number={wa_id}"
        response = f"For me to create and update Google Docs, I will need you to authorize me to access your Google Docs. Please do this at {login_url}" #TODO: Update URL and make it clickable
    # If
    else:
        # Check if the user has a document
        if get_most_recent_document(wa_id) is None:
            logging.info(f"User {wa_id} does not have a document")
            # Create a new document
            document_details = create_google_docs_document(credentials)
            document_title = document_details['title']
            document_id = document_details['document_id']
            # Store the document details in the database
            store_document_details(wa_id, document_title, document_id)
            document_content = get_google_doc(credentials, document_id)
        else:
            logging.info(f"User {wa_id} has a document")
            # Get the most recent document
            document = get_most_recent_document(wa_id)
            document_id = document['document_id']
            document_content = get_google_doc(credentials, document_id)
            response = generate_response(body, wa_id, document_content, credentials)
            #update_request = create_append_text_update_request(document_content, text_body)
            #batch_update_google_docs_document(credentials, document_id, update_request)
            

  

    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    # Extract the message & message type
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # Generate a response text message
    response = process_text_for_whatsapp(response)

    # Prepare Whatsapp JSON and send the message
    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
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
