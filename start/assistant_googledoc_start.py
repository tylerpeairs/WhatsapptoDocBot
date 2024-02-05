from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

assistant_instructions = """You're a helpful WhatsApp assistant that assists businesses in organizing their WhatsApp messages by inputing them into a Google Document and categorizing them. Use the provided Google Docs API function batch_update_google_docs_document and update the document according to the user's whatsapp message.

You will receive 3 variables:

1. whatsapp_text is the text content from the user's most recent whatsapp message. This is the text which will be added to the document.
2. document_content is the JSON object returned from Google's get document API which will need to be manipulated to insert the whatsapp_text in an organized and categorized format. You must extract the document_id from this and use it as part of your batch_update request.
3. user credentials is the credentials needed to post the batch update request

Here are the values for these 3 variables:
credentials: {credentials}
whatsapp_text: {whatsapp_text}
document_content: {document_content}

If you don't know how to categorize the message, ask the user to choose a category and provide 3 suggestions. Categorizations always correspond to a HEADING_1 namedStyleType. For example, let's say you received the following request:

Your response should always be in the format of:  

Google Docs Link: https://docs.google.com/document/d/{document_id}/edit
Categorized: {Categorization}  
Text Added: {Human Readable Format}  

Here's an example of a request and response:

credentials: user_credential_object
whatsapp_text: "got 300 pesos Tyler"
document_content: document_content_object

You will change the text to be more readable, so you might change it to "Received 300 pesos from Tyler", and you could categorize it under "Money Received". Then you make a corresponding batch update request where you input the new text under the Money Received categorization by using the batch_update_google_docs_document function. If there is existing text in the document_content, you must use that text as context, so you may not always need to create new categories but instead can add text under an existing category by referencing the index of the category and surrounding text. Additionally, you will not always categorize or add text at the beginning or the end of the document. Rather, read the document_content object and decide the most logical place to insert the new text and categories.

Your response may look like:
Google Docs Link: https://docs.google.com/document/d/example_document_id/edit
Categorized: "Money Received"
Text Added: "Received 300 pesos from Tyler" """

# Create thread database column
# Generate thread
# Generate response
# Generate a 10 edge and test cases



# --------------------------------------------------------------
# Create assistant
# --------------------------------------------------------------
def create_assistant(assistant_instructions):

    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp Google Doc Assistant",
        instructions=assistant_instructions,
        tools = [{
          "type": "function",
          "function": {
            "name": "batch_update_google_docs_document",
            "description": "Batch update a Google Docs document with specified update requests",
            "parameters": {
                "type": "object",
                "properties": {
                    "credentials": {"type": "object", "description": "The credentials needed to authenticate the Google Docs API request"},
                    "document_id": {"type": "string", "description": "The ID of the document to update"},
                    "update_requests": {
                        "type": "array",
                        "description": "A list of update requests to apply to the document",
                        "items": {
                            "type": "object",
                            "description": "An individual update request"
                        }
                    }
                },
                "required": ["credentials", "document_id", "update_requests"]
            }
        }
    }],
        model="gpt-4-1106-preview"
    )
    return assistant


#assistant = create_assistant(assistant_instructions)
#print(assistant)

# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


# --------------------------------------------------------------
# Generate response
# --------------------------------------------------------------
def generate_response(message_body, wa_id, document_content, credentials):
 

    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        print(f"Creating new thread for wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        print(f"Retrieving existing thread for wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    structured_message_content = {
        "body": message_body,  # Original message body
        "context": {
            "documentTitle": document_content,
            "credentials": credentials  # Be cautious with passing sensitive information
        }
    }
    
    # Convert structured_message_content to a string if necessary
    # Ensure your system handles this securely
    content_to_send = json.dumps(structured_message_content)
    print(f"Content to send: {content_to_send}")

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content_to_send, 
    )

    # Run the assistant and get the new message
    new_message = run_assistant(thread)
    print(f"To wa_id:", new_message)
    return new_message


# --------------------------------------------------------------
# Run assistant
# --------------------------------------------------------------
def run_assistant(thread):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve("asst_pXKz78pPXzb9LOg5N8Ta3JEf")

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Wait for completion
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    print(f"Generated message: {new_message}")
    return new_message


# --------------------------------------------------------------
# Test assistant
# --------------------------------------------------------------

message_body = {'object': 'whatsapp_business_account', 'entry': [{'id': '241544202367217', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15551294221', 'phone_number_id': '246316221888389'}, 'contacts': [{'profile': {'name': 'Tyler'}, 'wa_id': '12252781239'}], 'messages': [{'from': '12252781239', 'id': 'wamid.HBgLMTIyNTI3ODEyMzkVAgASGBYzRUIwODc1Q0IzQTQyRERBNzg5NDUxAA==', 'timestamp': '1707079705', 'text': {'body': 'Received 300 pesos from Tyler'}, 'type': 'text'}]}, 'field': 'messages'}]}]}
wa_id = '12252781239'
document_content = {'title': 'Whatsapp Notes 2024-02-04', 'body': {'content': [{'endIndex': 1, 'sectionBreak': {'sectionStyle': {'columnSeparatorStyle': 'NONE', 'contentDirection': 'LEFT_TO_RIGHT', 'sectionType': 'CONTINUOUS'}}}, {'startIndex': 1, 'endIndex': 2, 'paragraph': {'elements': [{'startIndex': 1, 'endIndex': 2, 'textRun': {'content': '\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}]}, 'documentStyle': {'background': {'color': {}}, 'pageNumberStart': 1, 'marginTop': {'magnitude': 72, 'unit': 'PT'}, 'marginBottom': {'magnitude': 72, 'unit': 'PT'}, 'marginRight': {'magnitude': 72, 'unit': 'PT'}, 'marginLeft': {'magnitude': 72, 'unit': 'PT'}, 'pageSize': {'height': {'magnitude': 792, 'unit': 'PT'}, 'width': {'magnitude': 612, 'unit': 'PT'}}, 'marginHeader': {'magnitude': 36, 'unit': 'PT'}, 'marginFooter': {'magnitude': 36, 'unit': 'PT'}, 'useCustomHeaderFooterMargins': True}, 'namedStyles': {'styles': [{'namedStyleType': 'NORMAL_TEXT', 'textStyle': {'bold': False, 'italic': False, 'underline': False, 'strikethrough': False, 'smallCaps': False, 'backgroundColor': {}, 'foregroundColor': {'color': {'rgbColor': {}}}, 'fontSize': {'magnitude': 11, 'unit': 'PT'}, 'weightedFontFamily': {'fontFamily': 'Arial', 'weight': 400}, 'baselineOffset': 'NONE'}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'alignment': 'START', 'lineSpacing': 115, 'direction': 'LEFT_TO_RIGHT', 'spacingMode': 'COLLAPSE_LISTS', 'spaceAbove': {'unit': 'PT'}, 'spaceBelow': {'unit': 'PT'}, 'borderBetween': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'borderTop': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'borderBottom': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'borderLeft': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'borderRight': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'indentFirstLine': {'unit': 'PT'}, 'indentStart': {'unit': 'PT'}, 'indentEnd': {'unit': 'PT'}, 'keepLinesTogether': False, 'keepWithNext': False, 'avoidWidowAndOrphan': True, 'shading': {'backgroundColor': {}}, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_1', 'textStyle': {'fontSize': {'magnitude': 20, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 20, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 6, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_2', 'textStyle': {'bold': False, 'fontSize': {'magnitude': 16, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 18, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 6, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_3', 'textStyle': {'bold': False, 'foregroundColor': {'color': {'rgbColor': {'red': 0.2627451, 'green': 0.2627451, 'blue': 0.2627451}}}, 'fontSize': {'magnitude': 14, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 16, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_4', 'textStyle': {'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}}, 'fontSize': {'magnitude': 12, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 14, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_5', 'textStyle': {'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}}, 'fontSize': {'magnitude': 11, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 12, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_6', 'textStyle': {'italic': True, 'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}}, 'fontSize': {'magnitude': 11, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 12, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'TITLE', 'textStyle': {'fontSize': {'magnitude': 26, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'unit': 'PT'}, 'spaceBelow': {'magnitude': 3, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'SUBTITLE', 'textStyle': {'italic': False, 'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}}, 'fontSize': {'magnitude': 15, 'unit': 'PT'}, 'weightedFontFamily': {'fontFamily': 'Arial', 'weight': 400}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'unit': 'PT'}, 'spaceBelow': {'magnitude': 16, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}]}, 'revisionId': 'ALBJ4LuoAyPklEPpAiZe4AILxJCjUnCTgIwacaGfcuyRF2Pbo7Sn3oLvxwe2rgLxOx3l9i3OIr_bHN6ISTOdZA', 'suggestionsViewMode': 'SUGGESTIONS_INLINE', 'documentId': '18niWChyLmbqGEyCLSbbnwFdt1b1e0Fk3y--FQDWaAEI'}
credentials = "<google.oauth2.credentials.Credentials object at 0x11386ccd0>"
new_message = generate_response(message_body, wa_id, document_content, credentials)

