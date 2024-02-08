# This file contains the functions to create a new Google Docs document, get the content of a Google Docs document, and batch update a Google Docs document.

# Import the required modules
from googleapiclient.discovery import build
from datetime import datetime

# Create a new Google Docs document
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

# Get the content of a Google Docs document
def get_google_doc_content(credentials, document_id):
    # Build the Google Docs service
    service = build('docs', 'v1', credentials=credentials)
    
    try:
        # Use the Google Docs service to get the specified document by ID
        document = service.documents().get(documentId=document_id).execute()
        doc_content = document.get('body').get('content')
        # Return the document object
        return doc_content
    except Exception as e:
        return None
    
# Batch update a Google Docs document with specified update requests
def batch_update_google_docs_document(credentials, document_id, update_requests):
    # Build the Google Docs service
    service = build('docs', 'v1', credentials=credentials)
    
    # Execute the batch update
    result = service.documents().batchUpdate(
        documentId=document_id,
        body=update_requests
    ).execute()
    
    # Print the result or return it for further processing
    print(f"Batch update completed. Result: {result}")
    return result

# Helper function to create an update request for inserting text
def create_update_requests(doc_content, category, text):
    # Helper function to create an update request for inserting text
    def insert_text_request(location, content, style):
        return {
            'insertText': {
                'location': {
                    'index': location
                },
                'text': content
            }
        }, {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': location,
                    'endIndex': location + len(content)
                },
                'paragraphStyle': {
                    'namedStyleType': style,
                },
                'fields': 'namedStyleType',
            }
        }

    existing_categories, end_index_of_last_paragraph = parse_existing_categories(doc_content)

    update_requests = []

    # Determine if the input category exists and where to insert the text
    if category in existing_categories:
        category_start_index = existing_categories[category]
        insert_position = category_start_index + len(category) + 1  # Include newline character

        # Iterate through document content to find the position right before the next HEADING_1 after the category
        for element in doc_content:
            if 'paragraph' in element and element.get('startIndex', 0) > category_start_index:
                paragraph_style = element['paragraph'].get('paragraphStyle', {}).get('namedStyleType')
                if paragraph_style == 'HEADING_1':
                    insert_position = element['startIndex']  # Position before the next HEADING_1
                    break

        print("Insert position:", insert_position)
        text_insert_request, text_style_request = insert_text_request(insert_position, text + '\n', 'NORMAL_TEXT')
        update_requests.extend([text_insert_request, text_style_request])

    else:
        # Category does not exist, create a new category at the end with HEADING_1 style
        # and insert the text underneath it with NORMAL_TEXT style
        if not existing_categories:
            category_string = category + '\n'
        else:
            category_string = '\n' + category + '\n'
        category_length = len(category_string) + 1  # Include newline character
        print("End index of last paragraph:", end_index_of_last_paragraph)
        category_insert_index = end_index_of_last_paragraph - 1
        print("Category insert index:", category_insert_index)
        category_insert_request, category_style_request = insert_text_request(category_insert_index, category_string, 'HEADING_1')
        text_insert_index = category_insert_index + category_length - 1
        print("Text insert index:", text_insert_index)
        text_insert_request, text_style_request = insert_text_request(text_insert_index, text + '\n', 'NORMAL_TEXT')
        update_requests.extend([category_insert_request, category_style_request, text_insert_request, text_style_request])

    return {'requests': update_requests}

# Get existing categories and index of last paragraph
def parse_existing_categories(doc_content):
    existing_categories = {}
    end_index_of_last_paragraph = 2
    contents = doc_content.get('content', [])

    # Parse the existing document structure to find HEADING_1 categories and their positions
    for content in contents:
        if 'paragraph' in content and 'paragraphStyle' in content['paragraph']:
            style = content['paragraph']['paragraphStyle'].get('namedStyleType')
            if style == 'HEADING_1':
                text_content = ''.join(element['textRun']['content'] for element in content['paragraph']['elements'])
                # Removing trailing newlines for comparison
                clean_text_content = text_content.rstrip('\n')
                existing_categories[clean_text_content] = content['startIndex']
        end_index_of_last_paragraph = max(end_index_of_last_paragraph, content.get('endIndex', 1))

    return existing_categories, end_index_of_last_paragraph