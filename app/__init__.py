# Description: This file is the main entry point for the application. It creates the Flask app and registers the blueprints.

#Import OS and Dotenv
import os

#Import app configurations and logging settings
from .config import load_configurations, configure_logging

#Import the database
from .extensions import db

#Import Flask and the database
from flask import Flask, redirect, request, session, url_for, json, render_template, jsonify

from werkzeug.exceptions import BadRequest


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #TODO bypass https requirement (REMOVE FOR PROD)

# Create the app
def create_app():

    
    # Create a Flask app
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Set a consistent secret key for session management

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        if request.content_type == 'application/json':
            # This assumes the BadRequest was due to JSON parsing
            return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400
        return e.get_response()

    
    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Set up the database  
    db.init_app(app)

    # Import models here to ensure they are known to SQLAlchemy
    from . import models

    # Register blueprints
    register_blueprints(app)


    return app

# Import blueprints to register
def register_blueprints(app):
    # Import blueprints
    from .blueprints.webhook_blueprint import webhook_blueprint
    from .blueprints.oauth_blueprint import oauth_blueprint

    # Register blueprints
    app.register_blueprint(webhook_blueprint)
    app.register_blueprint(oauth_blueprint)
    
