# This file contains the functions to create a new Google Docs document, get the content of a Google Docs document, and batch update a Google Docs document.

# Import the required modules
from calendar import c
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
    update_requests = []

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

    # Get end index of the last paragraph
    def find_insertion_index(existing_categories, category_name, doc_content):
        category_names = list(existing_categories.keys())
        print(existing_categories)

        if category_name in existing_categories:
            category_index = category_names.index(category_name)

            # Check if it's the last category
            if category_index == len(category_names) - 1:
                if 'paragraph' in doc_content[-1] and not doc_content[-1]['paragraph']['elements'][0]['textRun']['content'].strip():
                    # The last element is a newline, use its startIndex - 1
                    return doc_content[-1]['startIndex']
                else:
                    # No trailing newline, use the document's last element's endIndex - 1
                    return doc_content[-1]['endIndex'] - 1
                
            # Not the last category, use the next category's startIndex - 1
            else:
                # Not the last category, use the next category's startIndex - 1
                next_category_name = category_names[category_index + 1]
                next_category_start = existing_categories[next_category_name]['startIndex']
                return next_category_start - 1
            
        else:
            # Handle the case for a new category or text insertion at the end of the document
            last_content = doc_content[-1]
            
            # If the last content is a newline, use its startIndex as the insertion index
            # This effectively places the new category/text just before the trailing newline
            if last_content_is_newline(doc_content):
                return last_content['startIndex']
            
            # If the last content is not a newline, use the document's last element's endIndex
            # This adds the new category/text at the very end, even after the trailing newline if it exists
            return doc_content[-1]['endIndex']

    # Check if the last content is a newline
    def last_content_is_newline(doc_content):
        last_content = doc_content[-1]
        last_content_is_newline = False
        if 'paragraph' in last_content:
            last_paragraph_text = ''.join(element['textRun']['content'] for element in last_content['paragraph']['elements']).strip()
            last_content_is_newline = (last_paragraph_text == '')

        return last_content_is_newline
    
    # Parse for existing categories
    existing_categories = parse_existing_categories(doc_content)

    # Determine the insertion index for the new category and text
    insertion_index = find_insertion_index(existing_categories, category, doc_content)

    # Determine if the input category exists and where to insert the text
    if category in existing_categories:
        if last_content_is_newline(doc_content):
            text_insert_request, text_style_request = insert_text_request(insertion_index, text + '\n', 'NORMAL_TEXT')
        else:
            text_insert_request, text_style_request = insert_text_request(insertion_index, '\n' + text + '\n', 'NORMAL_TEXT')
        update_requests.extend([text_insert_request, text_style_request])
    else:
        # Category does not exist, create a new category at the end with HEADING_1 style
        category_string = '\n' + category + '\n' if existing_categories else category + '\n'
        category_length = len(category_string) + 1  # Include newline character
        category_insert_request, category_style_request = insert_text_request(insertion_index, category_string, 'HEADING_1')
       
        # and insert the text underneath it with NORMAL_TEXT style
        text_insert_index = insertion_index + category_length - 1
        text_insert_request, text_style_request = insert_text_request(text_insert_index, text + '\n', 'NORMAL_TEXT')
        
        update_requests.extend([category_insert_request, category_style_request, text_insert_request, text_style_request])

    return {'requests': update_requests}

# Get existing categories
def parse_existing_categories(doc_content):
    existing_categories = {}

    for content in doc_content:
        if 'paragraph' in content and 'paragraphStyle' in content['paragraph']:
            style = content['paragraph']['paragraphStyle'].get('namedStyleType')
            if style == 'HEADING_1':
                text_content = ''.join(element['textRun']['content'] for element in content['paragraph']['elements'])
                clean_text_content = text_content.rstrip('\n')
                if clean_text_content:
                    existing_categories[clean_text_content] = {
                        'startIndex': content['startIndex'],
                        'endIndex': content['endIndex']
                    }

    return existing_categories


