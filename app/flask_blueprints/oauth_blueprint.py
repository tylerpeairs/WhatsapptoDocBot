# This file contains the blueprint for the OAuth flow

# Import the required libraries
from turtle import st
from flask import Blueprint, session, redirect, url_for, render_template, request
from httpx import get
from app.utils.google_oauth_utils import get_credentials_from_session, get_authorization_url, fetch_token_and_store_in_session, CLIENT_CONFIG, SCOPES
from app.utils.whatsapp_utils import send_message, get_text_message_input
from app.database import store_document_details, store_user_credentials, get_most_recent_document
from app.utils.google_doc_utils import create_google_docs_document

# Create the blueprint
oauth_blueprint = Blueprint('oauth', __name__)

# Define the index route
@oauth_blueprint.route('/')
def index():

    # Check if the user has credentials in session
    if 'credentials' not in session:
        return redirect(url_for('oauth.login'))
    

    # Get the credentials from the session
    credentials = get_credentials_from_session(session)
    
    # Check if the user has been authenticated
    if session.get('authenticated'):
        # Display a success message
        wa_id = session.get('wa_id')
        print(f"wa_id at index: {session.get('wa_id')}")
        if wa_id:

            # Check if the user has a document
            if get_most_recent_document(wa_id) is None:
                
                # Create a new Google Doc
                document_details = create_google_docs_document(credentials)
                # Extract document_id and document_title from the returned dictionary
                document_id = document_details['document_id']
                document_title = document_details['document_title']
                # Store the document details in the database
                store_document_details(wa_id, document_title, document_id)
            else:
                # Get the most recent document
                document = get_most_recent_document(wa_id)
                print(f"Most recent document: {document}")
                document_title = document['title']
                document_id = document['document_id']
            # Prepare the success message
            success_message = f"Your most recent document is {document_title}. You can access it here: https://docs.google.com/document/d/{document_id}/edit. Message me to add more information."
            success_message_data = get_text_message_input(wa_id, success_message)
            send_message(success_message_data)
            return render_template('index.html', message="You have successfully authenticated Whatsapp to Doc Bot!")
        else:
            print(f"WA_ID not being passed")  # Debug print
            return redirect(url_for('oauth.login'))
    else:
        # Send the user to login if not authenticated
        return redirect(url_for('oauth.login'))



# Define the login route
@oauth_blueprint.route('/login')
def login():
    # Get the authorization URL
    authorization_url, state = get_authorization_url(CLIENT_CONFIG, SCOPES)
    # Retrieve the wa_id from 'number' query parameter
    wa_id = request.args.get('number', None)
    session['wa_id'] = wa_id
    # Explicitly save the session if necessary
    session.modified = True
    print(f"Session after setting state: {session}")  # Debug print

    return redirect(authorization_url)



# Define the callback route
@oauth_blueprint.route('/callback')
def callback():

    # Fetch the state from the session
    session_state = session.get('oauth_state')
    print(f"State from session: {session_state}")  # Debug print


    # Fetch the state returned in the callback URL
    callback_state = request.args.get('state')
    print(f"State from callback: {callback_state}")  # Debug print



    # Verify if the states match
    """if not session_state or session_state != callback_state:
        # Handle the error - states do not match
        return 'State validation failed', 403
"""
    # Fetch the token and store it in the session
    session_data = fetch_token_and_store_in_session(CLIENT_CONFIG, SCOPES)
    session.update(session_data)

    # Retrieve wa_id from session or parameter
    wa_id = session.get('wa_id')    
    print(f"wa_id during callback: {session.get('wa_id')}")

    # Set 'authenticated' to True after successful OAuth flow
    session['authenticated'] = True
    
    # Get tokens from the session data
    access_token = session_data.get('access_token')
    refresh_token = session_data.get('refresh_token')

    # Store refresh token in a secure location matching the wa_id
    store_user_credentials(wa_id, access_token, refresh_token)


    # Redirect to the index route to display the success message
    return redirect(url_for('oauth.index'))