#Import OS and Dotenv
import os
from dotenv import load_dotenv

#Import app configurations and logging settings
from app.config import load_configurations, configure_logging

#Import Flask and the database
from flask import Flask, redirect, request, session, url_for, json, render_template
from .views import webhook_blueprint
from flask_sqlalchemy import SQLAlchemy

#Import Google Oauth Libraries
from utils.google_oauth_utils import get_authorization_url, fetch_token_and_store_in_session, get_credentials_from_session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN") #TODO: Change to your domain in prod
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #TODO bypass https requirement (REMOVE FOR PROD)

# Initialize the database
db = SQLAlchemy()

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


# Create the app
def create_app():
    # Create a Flask app
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    # Set up the database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'  # Use your own database URI
    db.init_app(app)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    @app.route('/')
    def index():
        if 'credentials' not in session:
            return redirect(url_for('login'))
        
        credentials = get_credentials_from_session(session)
        
        # Check if the user has been authenticated
        if session.get('authenticated'):
            # Display a success message
            return render_template('index.html', message="You have successfully authenticated Whatsapp to Doc Bot!")
        else:
            return redirect(url_for('login'))
        # Use 'credentials' to make authorized API requests
        # ...

    @app.route('/login')
    def login():
        authorization_url, state = get_authorization_url(CLIENT_CONFIG, SCOPES)
        return redirect(authorization_url)

    @app.route('/callback')
    def callback():
        session_data = fetch_token_and_store_in_session(CLIENT_CONFIG, SCOPES)
        session.update(session_data)
        
        #TODO: Store refresh token in a secure location matching the wa_id

        return redirect(url_for('index'))
    


    return app