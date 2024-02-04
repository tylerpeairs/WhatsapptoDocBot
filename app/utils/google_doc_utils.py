from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime

def create_google_docs_document(credentials):
    # Get today's date in the desired format (e.g., YYYY-MM-DD)
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Combine "Whatsapp Notes" with today's date
    document_title = f"Whatsapp Notes {today_date}"
    
    # Build the Google Docs service
    service = build('docs', 'v1', credentials=credentials)
    
    # The body of the request containing the document title
    document = {
        'title': document_title
    }
    
    # Use the Google Docs service to create a new document
    doc = service.documents().create(body=document).execute()
    
    # Print the created document ID
    print(f"Created document with ID: {doc['documentId']}")
    
    # Return the document ID and title in a dictionary
    return {'document_id': doc['documentId'], 'document_title': document_title}


