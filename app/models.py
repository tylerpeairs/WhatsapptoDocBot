# Description: This file contains the models for the database.

# Import the required modules
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .extensions import db


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

    # Access Tokens Expire in 1 hour, so we need to store the time when the token was created to check for expiration and refresh requirements
    created_at = Column(DateTime, default=func.now())  # Automatically set at creation
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Automatically update
