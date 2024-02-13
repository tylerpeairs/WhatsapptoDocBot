# Description: This file contains the utility functions for Google OAuth 2.0

# Import the required modules
from flask import session
import json
import os
import secrets
from dotenv import load_dotenv
import logging

# Import the required Google OAuth 2.0 modules
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.exceptions import GoogleAuthError
from requests.exceptions import RequestException

# Load environment variabl8es
load_dotenv()
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
DOMAIN = os.getenv("NGROK_DOMAIN") #TODO: Change to your domain in prod


# Set up the Google OAuth 2.0 client & scopes
CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [f"https://{DOMAIN}/callback"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
}
SCOPES = ['https://www.googleapis.com/auth/documents']



# The redirect URI for the OAuth consent screen
def get_authorization_url(client_config, scopes):
    try:
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

    except KeyError as key_error:
        # Handle missing keys in the client_config dictionary
        logging.exception(f"KeyError: Missing key in client configuration - {key_error}")
        return None, None

    except GoogleAuthError as google_error:
        # Handle errors from the Google Auth library
        logging.exception(f"GoogleAuthError: {google_error}")
        return None, None

    except Exception as e:
        # Handle any other unexpected errors
        logging.exception(f"Unexpected error occurred: {e}")
        return None, None

def get_credentials_from_session(session):
    try:
        # Parse the JSON string in session['credentials'] back to a dictionary
        credentials_dict = json.loads(session['credentials'])
        
        # Attempt to create credentials object from the authorized user info
        credentials = Credentials.from_authorized_user_info(credentials_dict)
        
        # Check if credentials are valid, could add more checks here if needed
        if not credentials.valid:
            raise GoogleAuthError("The credentials have expired or are invalid.")
        
        return credentials
    
    except GoogleAuthError as e:
        # Handle errors from the Google authentication library
        logging.exception(f"Google authentication error occurred: {e}")
    
    except json.JSONDecodeError as e:
        # Handle JSON decoding errors (e.g., malformed JSON in 'session')
        logging.exception(f"Error decoding session credentials: {e}")
    
    except RequestException as e:
        # Handle network-related errors
        logging.exception(f"Network error occurred while handling OAuth: {e}")
    
    except Exception as e:
        # Handle all other exceptions
        logging.exception(f"An unexpected error occurred: {e}")


