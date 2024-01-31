from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from cryptography.fernet import Fernet
from .__init__ import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    wa_id = Column(String, unique=True)  # WhatsApp ID

    # Relationship to Credential
    credentials = relationship("Credential", backref="user", uselist=False)


class Credential(db.Model):
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    access_token = Column(String)
    refresh_token = Column(String)
