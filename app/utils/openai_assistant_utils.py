from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import json
from google.oauth2.credentials import Credentials
from app.database import store_thread, get_thread

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPEN_AI_API_KEY)


assistant_instructions = """You're a helpful WhatsApp assistant that assists businesses in organizing their WhatsApp messages by inputing them into a Google Document and categorizing them. Use the provided Google Docs API function batch_update_google_docs_document and update the document according to the user's whatsapp message.

You will receive 3 variables for the batch_update_google_docs_document function:

1. whatsapp_text is the text content from the user's most recent whatsapp message. This is the text which will be added to the document.
2. document_content is the JSON object returned from Google's get document API which will need to be manipulated to insert the whatsapp_text in an organized and categorized format. You must extract the document_id from this and use it as part of your batch_update request.
3. user credentials is the credentials needed to post the batch update request

Here are the values for these 3 variables:
credentials: {credentials}
whatsapp_text: {whatsapp_text}
document_content: {document_content}

If you don't know how to categorize the message, ask the user to choose a category and provide 3 suggestions. Categorizations always correspond to a HEADING_1 namedStyleType. Once you have a categorization, call the batch_update_google_docs_document function with these values. For example, let's say you received the following request:

Your response should always be in the format of:  

'Google Docs Link: https://docs.google.com/document/d/{document_id}/edit
Categorized: {Categorization}  
Text Added: {Human Readable Format}'

Here's an example of a request and response:

credentials: user_credential_object
whatsapp_text: "got 300 pesos Tyler"
document_content: document_content_object

You will change the text to be more readable, so you might change it to "Received 300 pesos from Tyler", and you could categorize it under "Money Received". Then you make a corresponding batch update request where you input the new text under the Money Received categorization by using the batch_update_google_docs_document function. If there is existing text in the document_content, you must use that text as context, so you may not always need to create new categories but instead can add text under an existing category by referencing the index of the category and surrounding text. Additionally, you will not always categorize or add text at the beginning or the end of the document. Rather, read the document_content object and decide the most logical place to insert the new text and categories.

Your response may look like:
'Google Docs Link: https://docs.google.com/document/d/example_document_id/edit
Categorized: "Money Received"
Text Added: "Received 300 pesos from Tyler"' """

# Generate a 10 edge and test cases



# --------------------------------------------------------------
# Create assistant
# --------------------------------------------------------------
def create_assistant(assistant_instructions):

    assistant = client.beta.assistants.create(
        name="WhatsApp Google Doc Assistant v0.2",
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
        model="gpt-3.5-turbo-0125"
    )
    return assistant


#assistant = create_assistant(assistant_instructions)
#print(assistant)

# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------
def check_if_thread_exists(wa_id):
    thread_id = get_thread(wa_id)
    if thread_id is None:
        return None
    else:
        return thread_id

# --------------------------------------------------------------
# Generate response
# --------------------------------------------------------------
def generate_response(message_body, wa_id, document_content, credentials):
 

    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)
    print(f"Thread ID: {thread_id}")

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
        delete_existing_runs(thread.id)

    # Prepare the structured message content
    whatsapp_text = message_body

    content_to_send = f"whatsapp_text: {whatsapp_text}, document_content: {document_content}, credentials: {credentials}"
    
    # Ensure your system handles this securely
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
    assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Wait for completion
    while run.status != "completed":
        #Check if the run requires action and the action is to submit tool outputs
        if run.status == 'requires_action' and run.required_action.type == 'submit_tool_outputs':
            create_tool_outputs(run)
        else:
            # Be nice to the API
            time.sleep(10)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        


    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    print(f"Generated message: {new_message}")
    return new_message



def create_tool_outputs(run):
    # Extract the first tool call ID from the required actions
    # Assuming there's at least one tool call in the list
    tool_call_id = run.required_action.submit_tool_outputs.tool_calls[0].id

    # Submit the tool outputs for the given thread ID and run ID
    # Note: Adjust the tool_outputs list as per your specific requirements
    response = client.beta.threads.runs.submit_tool_outputs(
        thread_id=run.thread_id,
        run_id=run.id,
        tool_outputs=[
            {
                "tool_call_id": tool_call_id,
                "output": json.dumps({
                    "success": True,
                    "message": "Document updated successfully.",
                })
            },
        ]
    )

    print(f"Tool outputs submitted. Response: {response}")




def delete_existing_runs(thread_id):
    # Remove any existing runs
    runs = client.beta.threads.runs.list(
        thread_id=thread_id
        )
    print(f"Runs: {runs.data}")
    for run in runs.data:
        if run.status != "cancelled":
            run = client.beta.threads.runs.cancel(
                thread_id=thread_id,
                run_id=run.id
                )
            print(f"Run cancelled: {run}")