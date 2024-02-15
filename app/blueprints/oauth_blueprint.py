# This file contains the blueprint for the OAuth flow

# Import the required libraries
from flask import Blueprint, session, redirect, url_for, render_template, request
from app.utils.google_oauth_utils import get_credentials_from_session, get_authorization_url, CLIENT_CONFIG, SCOPES, fetch_token_and_store_in_session
from app.utils.whatsapp_utils import send_message, get_text_message_input
from app.database import get_user_credentials, store_document_details, store_user_credentials, get_most_recent_document
from app.utils.google_doc_utils import create_google_docs_document
from google_auth_oauthlib.flow import Flow



import logging

# Create the blueprint
oauth_blueprint = Blueprint('oauth', __name__)


# Define the index route
@oauth_blueprint.route('/')
def index():
    try:
        wa_id = session.get('wa_id')
        logging.info(f"wa_id from session: {wa_id}")

        # Check if the user has credentials
        if not get_user_credentials(wa_id):
            logging.info("User does not have credentials")
            return redirect(url_for('oauth.login'))

        credentials = get_user_credentials(wa_id)
        logging.info(f"Credentials at index: {credentials}")
        if wa_id:
            document = get_most_recent_document(wa_id)
            if not document:
                logging.info("No document found")
                document_details = create_google_docs_document(credentials)
                document_id = document_details['document_id']
                document_title = document_details['document_title']
                # Store document details and send message logic here...
                store_document_details(wa_id, document_title, document_id)
            else:
                logging.info("Document found")
                # Get the most recent document
                document = get_most_recent_document(wa_id)
                document_title = document['title']
                document_id = document['document_id']
        else:
            # Send the user to login if no wa_id is found
            return redirect(url_for('oauth.login'))
        
        if not all([document_id, document_title]):
            raise ValueError("Document ID or Title missing")
        
        # Prepare the success message
        logging.info(f"Document ID: {document_id}")
        logging.info(f"Document Title: {document_title}")
        success_message = f"Your most recent document is {document_title}. Access it here: https://docs.google.com/document/d/{document_id}/edit. Any messages you send to me will go to this document."
        success_message_data = get_text_message_input(wa_id, success_message)
        send_message(success_message_data)
        return render_template('index.html', message="You have successfully authenticated Whatsapp to Doc Bot!")
    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {e}")


# Define the login route
@oauth_blueprint.route('/login')
def login():
    try:
        # Get the authorization URL
        try:
            authorization_url, state = get_authorization_url(CLIENT_CONFIG, SCOPES)
        except Exception as e:
            return f"An error occurred: {e}"
        
        # Retrieve the wa_id from 'number' query parameter
        wa_id = request.args.get('number', None)

        # Store the wa_id and state in the session
        session['wa_id'] = wa_id
        session['oauth_state'] = state  # Store the state in the session

        # Explicitly save the session if necessary
        session.modified = True

        return redirect(authorization_url)
    except Exception as e:
        return render_template('error.html', message=f"An error occurred during callback: {e}"), 403




# Define the callback route
@oauth_blueprint.route('/callback')
def callback():
    try:
        # Verify if the states match
        session_state = session.get('oauth_state')
        callback_state = request.args.get('state')   
        if not session_state or session_state != callback_state:
            # Handle the error - states do not match
            return 'State validation failed', 403

        # Retrieve wa_id from session or parameter
        wa_id = session.get('wa_id')    

        # Set 'authenticated' to True after successful OAuth flow
        session['authenticated'] = True

        try:
            # Create a new Flow instance
            flow = Flow.from_client_config(
                client_config=CLIENT_CONFIG,
                scopes=SCOPES,
                redirect_uri=CLIENT_CONFIG['web']['redirect_uris'][0]
            )

            # Assuming the authorization response is part of the current request URL
            flow.fetch_token(authorization_response=request.url)

            # Store the credentials in a secure server-side session or database
            credentials = flow.credentials
            logging.info(f"Credentials from flow: {credentials}")
            store_user_credentials(wa_id, credentials)


        except Exception as e:
            logging.info(f"An error occurred: {e}")
    
        return redirect(url_for('oauth.index'))
    except Exception as e:
        return render_template('error.html', message=f"An error occurred during callback: {e}"), 403


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}