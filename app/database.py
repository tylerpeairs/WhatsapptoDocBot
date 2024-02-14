from .extensions import db
from .models import User, Document, encrypt
from google.oauth2.credentials import Credentials
import logging

def get_user_credentials(wa_id):
    user = User.query.filter_by(wa_id=wa_id).first()
    logging.info(f"User: {user}")
    logging.info(f"User credentials: {user.serialized_credentials}")  
    if user and user.serialized_credentials:
        # `Credentials.from_authorized_user_info` expects.
        credentials_info = user.serialized_credentials
        
        # Convert the dictionary back into a Credentials object
        credentials = Credentials.from_authorized_user_info(credentials_info)
        
        return credentials
    
    return None


def store_user_credentials(wa_id, credentials):
    user = User.query.filter_by(wa_id=wa_id).first()
    if not user:
        user = User(wa_id=wa_id)
        db.session.add(user)
    user.serialized_credentials = credentials
    db.session.commit()
    logging.info(f"Stored credentials for user {wa_id}")

def store_document_details(user_id, title, document_id):
    user = User.query.filter_by(wa_id=user_id).first()
    if user:
        new_document = Document(user_id=user.id, title=title, document_id=document_id)
        db.session.add(new_document)
        db.session.commit()
    else:
        return "User not found."

def get_most_recent_document(user_id):
    user = User.query.filter_by(wa_id=user_id).first()
    if user:
        document = Document.query.filter_by(user_id=user.id).order_by(Document.created_at.desc()).first()
        if document:
            return {
                'title': document.title,
                'document_id': document.document_id,
                'created_at': document.created_at.isoformat()
            }
    return None

def update_token_usage(wa_id, usage):
    user = User.query.filter_by(wa_id=wa_id).first()
    if user:
        user.token_usage = user.token_usage + usage if user.token_usage else usage
        db.session.commit()
    else:
        print("User not found.")
