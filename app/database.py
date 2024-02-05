# This file is used to create the database object that will be used to interact with the database

# Import the required modules
from sqlalchemy import true
from sqlalchemy.exc import SQLAlchemyError
import logging

# Import models
from .models import User, Document
from .extensions import db

# Import JSON
import json

# Import OAuth2Credentials
from google.oauth2.credentials import Credentials


# Get user credentials
def get_user_credentials(wa_id):
    # Query the user by wa_id along with their credentials
    logging.debug(f"Querying for user with wa_id: {wa_id}")
    user = User.query.filter_by(wa_id=wa_id).first()
    if user:
        logging.debug(f"User found with wa_id: {wa_id}")
        # User exists and has associated credentials
        unserialized_credentials = json.loads(user.serialized_credentials)
        return Credentials.from_authorized_user_info(unserialized_credentials)
    else:
        # User does not exist
        logging.debug(f"No user found with wa_id: {wa_id}")
        return None

# Store user credentials
def store_user_credentials(wa_id, credentials):

    # Query the user by wa_id
    logging.debug(f"Querying for user with wa_id: {wa_id}")
    user = User.query.filter_by(wa_id=wa_id).first()

    if user:
        # User exists, update their credentials
        logging.debug(f"User found with wa_id: {wa_id}, updating credentials")
        user.serialized_credentials = credentials.to_json()
    else:
        # User does not exist, create a new user
        logging.debug(f"No user found with wa_id: {wa_id}, creating new user")
        user = User(wa_id=wa_id, serialized_credentials=credentials.to_json())
        db.session.add(user)

    # Commit the changes to the database
    db.session.commit()
    logging.debug(f"Stored credentials for user with wa_id: {wa_id}")
        


# Store document details after using Google Docs API create call. user_id will be wa_id
def store_document_details(user_id, title, document_id):
    # Create a new Document instance with the provided details
    new_document = Document(user_id=user_id, title=title, document_id=document_id)
    
    # Add the new document to the session and commit it to the database
    db.session.add(new_document)
    db.session.commit()
    
    print(f"Document {title} with ID {document_id} stored in database.")

# Get the document details from the database using the wa_id
def get_most_recent_document(user_id):
    # Query the Document table for the most recent document related to the user_id
    document = Document.query.filter_by(user_id=user_id).order_by(Document.created_at.desc()).first()

    # If a document is found, prepare the details
    if document:
        document_details = {
            'title': document.title,
            'document_id': document.document_id,
            'created_at': document.created_at  # Optionally include the creation timestamp
        }
        return document_details
    else:
        # Return None or an appropriate message if no document is found
        return None
    

# Store thread_id for a wa_id
def store_thread(wa_id, thread_id):
    user = User.query.filter_by(wa_id=wa_id).first()
    user.thread_id = thread_id
    db.session.commit()
    print(f"Stored thread_id for user with wa_id: {wa_id}")

# Get thread_id for a wa_id
def get_thread(wa_id):
    user = User.query.filter_by(wa_id=wa_id).first()
    return user.thread_id
    print(f"Retrieved thread_id: {thread_id} for user with wa_id: {wa_id}")


# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------
def check_if_thread_exists(wa_id):
    thread_id = get_thread(wa_id)
    if thread_id is None:
        return None
    else:
        return thread_id