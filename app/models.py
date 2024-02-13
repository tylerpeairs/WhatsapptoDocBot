from .extensions import db   
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func
import os
from google.oauth2.credentials import Credentials
import json

Base = declarative_base()

def get_secret_key():
    key = os.getenv('PGCRYPTO_KEY')
    if not key:
        raise ValueError("Secret key not set in environment variables")
    return key

# Utility functions for encryption and decryption
def encrypt(expr):
    """Encrypt an expression (value) with a secret key."""
    secret_key = os.getenv('PGCRYPTO_KEY')  # Ensure you've set this environment variable
    return func.pgp_sym_encrypt(expr, secret_key)

def decrypt(column):
    """Decrypt a column with a secret key."""
    secret_key = os.getenv('PGCRYPTO_KEY')
    return func.pgp_sym_decrypt(column, secret_key).label(column.name)



class User(db.Model):


    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    wa_id = db.Column(db.Text, unique=True)  # Store WhatsApp ID directly without encryption
    _serialized_credentials = db.Column('serialized_credentials', db.Text)  # Encrypted Google credentials
    token_usage = db.Column('token_usage', db.Text)  # Encrypted token usage

    @hybrid_property
    def serialized_credentials(self):
        if self._serialized_credentials:
            decrypted_data = decrypt(self._serialized_credentials)
            return json.loads(decrypted_data)
        return None

    @serialized_credentials.setter
    def serialized_credentials(self, credentials):
        self._serialized_credentials = encrypt(credentials.to_json())
        

    # Relationship to Document
    documents = db.relationship('Document', backref='user', lazy=True)


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String)  # Assume title is not encrypted
    document_id = db.Column('document_id', db.Text)  # Encrypted document ID
    created_at = db.Column(db.DateTime, default=func.now())  # Timestamp of creation