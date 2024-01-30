from flask import Flask, redirect, request, session, url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Replace these with your actual client ID and client secret
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

# The OAuth scopes you need
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# Client Configuration
CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["http://localhost:8000/callback"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
}

def create_app():
    # Create a Flask app
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    @app.route('/')
    def index():
        if 'credentials' not in session:
            return redirect(url_for('login'))
        credentials = Credentials.from_authorized_user_info(session['credentials'])
        # Use 'credentials' to make authorized API requests
        # ...

    @app.route('/login')
    def login():
        # Note: REDIRECT_URI needs to be defined here in each function where it's used

        flow = Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=CLIENT_CONFIG['web']['redirect_uris'][0]
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
        )

        # Store the state so you can verify the response.
        session['state'] = state

        return redirect(authorization_url)

    @app.route('/callback')
    def callback():
        REDIRECT_URI = url_for('callback', _external=True)

        # Check if the state parameter in the response matches the stored state
        if 'state' not in session or request.args.get('state') != session['state']:
            return 'State mismatch. Please try again.'

        flow = Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=SCOPES,
            state=state,
            redirect_uri=CLIENT_CONFIG['web']['redirect_uris'][0]
        )

        flow.fetch_token(authorization_response=request.url)

        # Store the credentials in the session
        credentials = flow.credentials
        session['credentials'] = credentials.to_json()

        return redirect(url_for('index'))

    return app
