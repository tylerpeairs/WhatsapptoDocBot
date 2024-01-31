#import the required libraries
from flask import Blueprint, session, redirect, url_for, render_template
from .auth import get_credentials_from_session, get_authorization_url, CLIENT_CONFIG, SCOPES #Can I import config and scopes directly from oauth_utils?

oauth_blueprint = Blueprint('oauth', __name__)

@oauth_blueprint.route('/')
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

@oauth_blueprint.route('/login')
def login():
    authorization_url, state = get_authorization_url(CLIENT_CONFIG, SCOPES)
    return redirect(authorization_url)

@oauth_blueprint.route('/callback')
def callback():
    session_data = fetch_token_and_store_in_session(CLIENT_CONFIG, SCOPES)
    session.update(session_data)
    
    #TODO: Store refresh token in a secure location matching the wa_id

    return redirect(url_for('index'))