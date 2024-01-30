from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from cryptography.fernet import Fernet

Base = declarative_base()

class Credential(Base):
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True)
    encrypted_token = Column(String)

    @validates('encrypted_token')
    def validate_encrypted_token(self, key, encrypted_token):
        # Encrypt the token before storing it
        fernet = Fernet('<your-encryption-key>')
        return fernet.encrypt(encrypted_token.encode()).decode()

    def decrypt_token(self):
        # Decrypt the token when needed
        fernet = Fernet('<your-encryption-key>')
        return fernet.decrypt(self.encrypted_token.encode()).decode()
