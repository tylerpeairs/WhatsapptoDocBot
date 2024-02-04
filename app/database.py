# This file is used to create the database object that will be used to interact with the database

# Import the required modules
from sqlalchemy import true
from sqlalchemy.exc import SQLAlchemyError

# Import models
from .models import User, Credential, Document
from .extensions import db


# Get user credentials
def get_user_credentials(wa_id):
    # Query the user by wa_id along with their credentials
    user = User.query.filter_by(wa_id=wa_id).first()
    if user and user.credentials:
        # User exists and has associated credentials
        return {
            'exists': True,
            'access_token': user.credentials.access_token,
            'refresh_token': user.credentials.refresh_token,
            'created_at': user.credentials.created_at,
            'updated_at': user.credentials.updated_at
        }
    else:
        # User does not exist or has no credentials
        return {'exists': False}
    

def store_user_credentials(wa_id, access_token, refresh_token):
    """
    Store a new user's WhatsApp ID and OAuth tokens in the database with error handling.

    Parameters:
    - wa_id: The WhatsApp ID of the user.
    - access_token: The OAuth access token for the user.
    - refresh_token: The OAuth refresh token for the user.
    """
    try:
        # Start a transaction
        with db.session.begin():
            # Create a new User record
            user = User(wa_id=wa_id)
            db.session.add(user)
            
            # Flush the session to assign an ID to the user without committing the transaction. This gives the credential table.
            db.session.flush()

            # Create and link new Credential record to this user
            credentials = Credential(user_id=user.id, access_token=access_token, refresh_token=refresh_token)
            db.session.add(credentials)

        # Commit the transaction
        db.session.commit()

        # Return the user object for further processing or confirmation if needed
        return user
    except SQLAlchemyError as e:
        # Roll back the session to undo any partial changes due to the exception
        db.session.rollback()
        
        # Log the exception or handle it as needed for your application's requirements
        print(f"Failed to store user credentials: {e}")  # Consider using logging instead of print for production applications
        

# Update the access token in the database
def update_access_token(wa_id, access_token):
    """
    Store a new user's access token after refresh in the database with error handling.

    Parameters:
    - wa_id: The WhatsApp ID of the user.
    - access_token: The OAuth access token for the user.
    """
    try:
        # Start a transaction
        with db.session.begin():
            # Create a new User record
            user_to_update = session.query(User).filter(User.wa_id).one()

            #Update the auth token
            user_to_update.credentials.access_token = access_token
        # Commit the transaction
        db.session.commit()

        # Return the user object for further processing or confirmation if needed
    except SQLAlchemyError as e:
        # Roll back the session to undo any partial changes due to the exception
        db.session.rollback()
        
        # Log the exception or handle it as needed for your application's requirements
        print(f"Failed to store user credentials: {e}")  #

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
 