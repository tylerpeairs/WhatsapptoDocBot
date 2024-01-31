# Description: This file contains the models for the database.

# Import the required modules
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates, relationship
from cryptography.fernet import Fernet
from .database import db

# Create the User class
class User(db.Model):
    # Define the user table name
    __tablename__ = 'users'
    # Define the user table columns
    id = Column(Integer, primary_key=True)
    wa_id = Column(String, unique=True)  # WhatsApp ID

    # Relationship to Credential
    credentials = relationship("Credential", backref="user", uselist=False)

# Create the Credential class
class Credential(db.Model):
    # Define the credential table name
    __tablename__ = 'credentials'

    # Define the credential table columns
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    access_token = Column(String)
    refresh_token = Column(String)
