# Description: This file contains the utility functions for Google OAuth 2.0

# Import the required modules
from flask import request, session
import json
import os
import secrets
from dotenv import load_dotenv

# Import the required Google OAuth 2.0 modules
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN") #TODO: Change to your domain in prod


# Set up the Google OAuth 2.0 client & scopes
CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [f"https://{NGROK_DOMAIN}/callback"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
}
SCOPES = ['https://www.googleapis.com/auth/documents']



# The redirect URI for the OAuth consent screen
def get_authorization_url(client_config, scopes):

    # Create a unique state value
    state = secrets.token_urlsafe()

    # Store the state in the session for later verification
    session['oauth_state'] = state


    # Create a new Flow instance
    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=scopes,
        redirect_uri=client_config['web']['redirect_uris'][0]
    )

    # Generate the authorization URL
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        state=state
    )

    return authorization_url, state

def get_credentials_from_session(session):
    # Parse the JSON string in session['credentials'] back to a dictionary
    credentials_dict = json.loads(session['credentials'])
    credentials = Credentials.from_authorized_user_info(credentials_dict)
    return credentials

def fetch_token_and_store_in_session(client_config, scopes):
    # Create a new Flow instance
    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=scopes,
        redirect_uri=client_config['web']['redirect_uris'][0]
    )


    # Fetch the token
    flow.fetch_token(authorization_response=request.url)

    # Store the credentials in the session
    credentials = flow.credentials
    session_data = {
        'credentials': credentials.to_json(),
        'access_token': credentials.token,
        'refresh_token': credentials.refresh_token
    }

    return session_data

def refresh_access_token():
    # Load the stored refresh token
    # TODO: Load the stored refresh token
    #refresh_token = ...

    # Create a new flow instance and refresh the token
    flow = Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=CLIENT_CONFIG['web']['redirect_uris'][0]
    )
    flow.refresh_token(refresh_token)
    new_credentials = flow.credentials

    # Store the new credentials in the session
    session['credentials'] = new_credentials.to_json()
    # Store the access token in the session
    session['access_token'] = new_credentials.token



    return new_credentials