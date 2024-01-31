# This file contains decorators to ensure that the incoming requests to our webhook are valid and signed with the correct signature.

# Import the required modules
from functools import wraps
from flask import current_app, jsonify, request
import logging
import hashlib
import hmac

# Validate the incoming payload's signature against our expected signature
def validate_signature(payload, signature):

    # Use the App Secret to hash the payload
    expected_signature = hmac.new(
        bytes(current_app.config["APP_SECRET"], "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Check if the signature matches
    return hmac.compare_digest(expected_signature, signature)

# Decorator to ensure that the incoming requests to our webhook are valid and signed with the correct signature.
def signature_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get("X-Hub-Signature-256", "")[
            7:
        ]  # Removing 'sha256='
        if not validate_signature(request.data.decode("utf-8"), signature):
            logging.info("Signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403
        return f(*args, **kwargs)

    return decorated_function
