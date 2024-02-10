# Description: This file contains the utility functions for Google OAuth 2.0

# Import the required modules
from flask import session
import json
import os
import secrets
from dotenv import load_dotenv

# Import the required Google OAuth 2.0 modules
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Load environment variabl8es
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

# Get the credentials from the authorization code
def get_credentials_from_session(session):
    # Parse the JSON string in session['credentials'] back to a dictionary
    credentials_dict = json.loads(session['credentials'])
    credentials = Credentials.from_authorized_user_info(credentials_dict)
    return credentials



