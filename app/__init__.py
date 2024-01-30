from flask import Flask, redirect, request, session, url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint

#Create db
db = SQLAlchemy()

# Load environment variables
load_dotenv()

# Replace these with your actual client ID and client secret
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

# The OAuth scopes you need
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

#Ngrok Domain
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")


# Client Configuration
CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [f"https://{NGROK_DOMAIN}/callback"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
}

def create_app():
    # Create a Flask app
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    # Set up the database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'  # Use your own database URI
    db.init_app(app)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    #Ngrok Domain



    @app.route('/')
    def index():
        if 'credentials' not in session:
            return redirect(url_for('login'))
        credentials = Credentials.from_authorized_user_info(session['credentials'])

        # Check if the user has been authenticated
        if session.get('authenticated'):
            # Display a success message
            return render_template('index.html', message="You have successfully logged in!")
        else:
            return redirect(url_for('login'))
        # Use 'credentials' to make authorized API requests
        # ...

    @app.route('/login')
    def login():
        flow = Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=CLIENT_CONFIG['web']['redirect_uris'][0]
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
        )

        return redirect(authorization_url)

    @app.route('/callback')
    def callback():
        REDIRECT_URI = f"https://{NGROK_DOMAIN}/callback"

        flow = Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=CLIENT_CONFIG['web']['redirect_uris'][0]
        )

        flow.fetch_token(authorization_response=request.url)

        # Store the credentials in the session
        credentials = flow.credentials
        session['credentials'] = credentials.to_json()
        

        return redirect(url_for('index'))

    return app