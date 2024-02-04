# Description: This file contains the models for the database.

# Import the required modules
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .extensions import db


Base = declarative_base()


# Create the User class
class User(db.Model):
    # Define the user table name
    __tablename__ = 'users'
    # Define the user table columns
    id = Column(Integer, primary_key=True)
    wa_id = Column(String, unique=True)  # WhatsApp ID
    serialized_credentials = Column(Text)  # Store serialized Google credentials as a JSON string

    # Relationship to Document
    documents = relationship("Document", backref="user")



class Document(db.Model):
    __tablename__ = 'documents'
    
    # Columns
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    document_id = Column(String)
    created_at = Column(DateTime, default=func.now())  # Timestamp of creation

    
    # Relationship to User
    user = relationship("User", backref="documents")



