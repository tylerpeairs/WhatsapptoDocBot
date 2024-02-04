# This file is used to create the database object that will be used to interact with the database

# Import the required modules
from sqlalchemy import true
from sqlalchemy.exc import SQLAlchemyError

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
    user = User.query.filter_by(wa_id=wa_id).first()
    if user and user.credentials:
        # User exists and has associated credentials
        unserialized_credentials = json.loads(user.credentials)
        return Credentials.from_authorized_user_info(unserialized_credentials)
    else:
        # User does not exist or has no credentials
        return {'exists': False}


# Store a new user's WhatsApp ID and OAuth credentials in the database with error handling.
def store_user_credentials(wa_id, credentials):
    try:
        # Start a transaction
        with db.session.begin():
            # Create a new User record
            user = User(wa_id=wa_id)
            db.session.add(user)
            
            # Flush the session to assign an ID to the user without committing the transaction. This gives the credential table.
            db.session.flush()

            # Create and link new Credential record to this user
            serialized_credentials = credentials.to_json()
            db.session.add(serialized_credentials)

        # Commit the transaction
        db.session.commit()

        # Return the user object for further processing or confirmation if needed
        return user
    except SQLAlchemyError as e:
        # Roll back the session to undo any partial changes due to the exception
        db.session.rollback()
        
        # Log the exception or handle it as needed for your application's requirements
        print(f"Failed to store user credentials: {e}")  # Consider using logging instead of print for production applications
        


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
 