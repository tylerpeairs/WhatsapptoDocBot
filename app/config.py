# Description: This file is used to load the configurations from the .env file and set the logging level for the application.

# Import the required modules
import sys
import os
from dotenv import load_dotenv
import logging

# Load the configurations
def load_configurations(app):
    load_dotenv()
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["YOUR_PHONE_NUMBER"] = os.getenv("YOUR_PHONE_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["PHONE_NUMBER_ID"] = os.getenv("PHONE_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'  #TODO:Change to your own database URI
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_SECURE'] = True  # Secure remember me cookie.
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True  # HTTPOnly remember me cookie.
    app.config['APP_DOMAIN'] = 'https://deciding-werewolf-infinitely.ngrok-free.app'


# Set up the logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
