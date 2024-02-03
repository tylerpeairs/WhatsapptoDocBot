from google_auth_oauthlib.flow import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import pickle
import os.path



def create_document(title, access_token):
    """Shows basic usage of the Docs API. Creates a document with the given title."""

    service = build('docs', 'v1', credentials=access_token)

    # Create a new document
    document = service.documents().create(body={'title': title}).execute()
    print('Created document with title: {0} (ID: {1})'.format(document.get('title'), document.get('documentId')))

if __name__ == '__main__':
    current_date = datetime.now().strftime("%Y-%m-%d")
    document_title = f"Document {current_date}"
    create_document(document_title)
