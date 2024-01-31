# This file contains the blueprint for the OAuth flow

# Import the required libraries
from flask import Blueprint, session, redirect, url_for, render_template, request
from app.utils.google_oauth_utils import get_credentials_from_session, get_authorization_url, fetch_token_and_store_in_session, CLIENT_CONFIG, SCOPES

# Create the blueprint
oauth_blueprint = Blueprint('oauth', __name__)

# Define the index route
@oauth_blueprint.route('/')
def index():

    # Check if the user has credentials in session
    if 'credentials' not in session:
        return redirect(url_for('oauth.login'))
    

    # Get the credentials from the session. It's a dict with the refresh and access tokens.
    credentials = get_credentials_from_session(session)
    
    # Check if the user has been authenticated
    if session.get('authenticated'):
        # Display a success message
        return render_template('index.html', message="You have successfully authenticated Whatsapp to Doc Bot!")
    else:
        # Send the user to login if not authenticated
        return redirect(url_for('oauth.login'))



# Define the login route
@oauth_blueprint.route('/login')
def login():
    # Get the authorization URL
    authorization_url, state = get_authorization_url(CLIENT_CONFIG, SCOPES)

    # Explicitly save the session if necessary
    session.modified = True
    print(f"Session after setting state: {session}")  # Debug print

    return redirect(authorization_url)



# Define the callback route
@oauth_blueprint.route('/callback')
def callback():
    print(f"Session at start of callback: {session}") 

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

    # Set 'authenticated' to True after successful OAuth flow
    session['authenticated'] = True
    
    #TODO: Store refresh token in a secure location matching the wa_id

    # Redirect to the index route to display the success message
    return redirect(url_for('oauth.index'))