from .extensions import db   
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func
from dotenv import load_dotenv
import os
import json
import logging
from cryptography.fernet import Fernet
import base64

load_dotenv()
Base = declarative_base()

def get_secret_key():
    key = os.getenv('FERNET_KEY')
    if not key:
        raise ValueError("Secret key not set in environment variables")
    return key


def encrypt(expr):
    """Encrypt an expression (value) with a secret key."""
    fernet = Fernet(get_secret_key())
    return fernet.encrypt(expr.encode()).decode()

def decrypt(encrypted_data):
    """Decrypt a column with a secret key."""
    fernet = Fernet(get_secret_key())
    return fernet.decrypt(encrypted_data.encode()).decode()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    wa_id = db.Column(db.Text, unique=True)
    _serialized_credentials = db.Column('serialized_credentials', db.Text)
    token_usage = db.Column('token_usage', db.Integer)

    @hybrid_property
    def serialized_credentials(self):
        if self._serialized_credentials:
            try:
                encrypted_data = self._serialized_credentials
                decrypted_data = decrypt(encrypted_data)
                return json.loads(decrypted_data)
            except Exception as e:
                logging.error(f"Error decrypting serialized credentials: {e}")
                return None
        return None

    @serialized_credentials.setter
    def serialized_credentials(self, credentials):
        serialized_json = credentials.to_json()  # Directly use json.dumps here
        self._serialized_credentials = encrypt(serialized_json)

        

    # Relationship to Document
    documents = db.relationship('Document', backref='user', lazy=True)


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String)  # Assume title is not encrypted
    document_id = db.Column('document_id', db.Text)  # Encrypted document ID
    created_at = db.Column(db.DateTime, default=func.now())  # Timestamp of creation