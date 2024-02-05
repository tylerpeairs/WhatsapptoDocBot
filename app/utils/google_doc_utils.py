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


def get_google_doc(credentials, document_id):
    # Build the Google Docs service
    service = build('docs', 'v1', credentials=credentials)
    
    try:
        # Use the Google Docs service to get the specified document by ID
        document = service.documents().get(documentId=document_id).execute()
        
        # Print some information about the document
        print(f"Document retrieved successfully: {document['title']} (ID: {document['documentId']})")
        
        # Return the document object
        return document
    except Exception as e:
        # If an error occurs, print it and return None
        print(f"Error retrieving document: {e}")
        return None
    

def batch_update_google_docs_document(credentials, document_id, update_requests):
    # Build the Google Docs service
    service = build('docs', 'v1', credentials=credentials)
    
    # Execute the batch update
    result = service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': update_requests}
    ).execute()
    
    # Print the result or return it for further processing
    print(f"Batch update completed. Result: {result}")
    return result


"""
1. Create an assistant which we can pass document_content, credentials, whatsapp message, and the document_id
2. Have this assistant take the document_content and whatsapp message to create an text_update_request
3. Have this assistant call the batch_update_google_docs_document function with the text_update_request
4. Send a whatsapp message confirming the batch update
"""

"""
def create_append_text_update_request(document, append_text):
    # The document structure indicates that the content ends at 'endIndex: 2' for the initial content.
    # To append text at the end of the document, use the highest endIndex found in the document's content.
    # For simplicity, this example assumes appending after the given endIndex of the last content piece.
    # In a dynamic scenario, you'd iterate over document['body']['content'] to find the actual highest endIndex.
    
    # Assuming the structure always has the endIndex in the last paragraph element
    # Note: This might need adjustment based on actual document content structure
    last_content_piece = document['body']['content'][-1]
    end_index = last_content_piece.get('endIndex', 1) - 1 # Default to 1 if not found

    
    update_request = [
        {
            "insertText": {
                "location": {
                    "index": end_index,
                },
                "text": append_text
            }
        }
    ]
    
    return update_request
"""