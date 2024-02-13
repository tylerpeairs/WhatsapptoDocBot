import hashlib
from .extensions import db
from .models import User, Document

def generate_hash(value):
    """Generate a SHA-256 hash of the given value."""
    return hashlib.sha256(value.encode()).hexdigest()

def get_user_credentials(wa_id):
    wa_id_hash = generate_hash(wa_id)
    user = User.query.filter_by(wa_id_hash=wa_id_hash).first()
    return user.credentials if user else None

def store_user_credentials(wa_id, credentials):
    wa_id_hash = generate_hash(wa_id)
    user = User.query.filter_by(wa_id_hash=wa_id_hash).first()
    if not user:
        user = User(wa_id=wa_id, wa_id_hash=wa_id_hash)
        db.session.add(user)
    user.credentials = credentials
    db.session.commit()

def store_document_details(user_id, title, document_id):
    wa_id_hash = generate_hash(user_id)
    user = User.query.filter_by(wa_id_hash=wa_id_hash).first()
    if user:
        new_document = Document(user_id=user.id, title=title, document_id=document_id)
        db.session.add(new_document)
        db.session.commit()
    else:
        return "User not found."

def get_most_recent_document(user_id):
    wa_id_hash = generate_hash(user_id)
    user = User.query.filter_by(wa_id_hash=wa_id_hash).first()
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
    wa_id_hash = generate_hash(wa_id)
    user = User.query.filter_by(wa_id_hash=wa_id_hash).first()
    if user:
        user.token_usage = user.token_usage + usage if user.token_usage else usage
        db.session.commit()
    else:
        print("User not found.")
