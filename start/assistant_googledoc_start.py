from openai import OpenAI
from dotenv import load_dotenv
import sys
import os
import time
import json
import shelve

import sys
import os



load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPEN_AI_API_KEY)

assistant_instructions = """You're a helpful WhatsApp assistant that assists businesses in organizing their WhatsApp messages by inputing them into a Google Document and categorizing them. Use the provided Google Docs API function batch_update_google_docs_document and update the document according to the user's whatsapp message. You will ALWAYS call the batch_update_google_docs_document function for every message.

You will receive a document_content object and a whatsapp_text:

1. whatsapp_text is the text content from the user's most recent whatsapp message. This is the text which will be added to the document.
2. document_content is the JSON object returned from Google's get document API which will need to be manipulated to insert the whatsapp_text in an organized and categorized format.

Here are the values for these 2 variables:
whatsapp_text: {whatsapp_text}
document_content: {document_content}

You should ALWAYS try to categorize the text. Categorizations always correspond to a "HEADING_1" namedStyleType. DO NOT change the namedStyleType input to other forms such as heading1 - it should always be HEADING_1. Once you have a categorization, you can call the batch_update_google_docs_document function with these values.

Here's an example of a request and response:

whatsapp_text: "got 300 pesos Tyler"
document_content: document_content_object

You will change the text to be more readable, so you might change it to "Received 300 pesos from Tyler", and you could categorize it under "Money Received". Then you make a corresponding batch update request where you input the new text under the Money Received categorization by using the batch_update_google_docs_document function. If there is existing text in the document_content, you must consider that text in your produced update_requests, so you may not always need to create new categories but instead can add text under an existing category by referencing the index of the category and surrounding text. Additionally, you will not always categorize or add text at the beginning or the end of the document. Rather, read the document_content object and decide the most logical place to insert the new text and categories, then create the update_requests object. You will only ever pass the update_requests object and NEVER pass the document_content or other objects when you call the batch_update_google_docs_document tool_call. Here's an example of an update_requests object with this whatsapp_text:
Any insertion index MUST BE less than the document_content endIndex. If you try to insert text at an index greater than the endIndex, the request will fail.

For example, a simplified document_content content object:
    {"content":[{"type":"sectionBreak","style":"CONTINUOUS","endIndex":1},{"type":"paragraph","text":"\\n","style":"NORMAL_TEXT","startIndex":1,"endIndex":2}]}

May yield an update_requests object like this where the index to insertText in the update_requests is ALWAYS lower than the endIndex in the content object:

{"update_requests":[{"insertText":{"location":{"index":1},"text":"Money Received\n"}},{"updateParagraphStyle":{"range":{"startIndex":1,"end

After succesfully passing this update_request, your response may look like:
'Google Docs Link: https://docs.google.com/document/d/example_document_id/edit
Categorized: "Money Received"
Text Added: "Received 300 pesos from Tyler"' """

# Create assistant
def create_assistant(assistant_instructions):

    assistant = client.beta.assistants.create(
        name="WhatsApp Google Doc Assistant v1.0",
        instructions=assistant_instructions,
        tools = [{
          "type": "function",
          "function": {
            "name": "batch_update_google_docs_document",
            "description": "Batch update a Google Docs document with specified update requests",
            "parameters": {
                "type": "object",
                "properties": {
                    "update_requests": {
                        "type": "array",
                        "description": "A list of update requests to apply to the document",
                        "items": {
                            "type": "object",
                            "description": "An individual update request"
                        }
                    }
                },
                "required": ["update_requests"]
            }
        }
    }],
        model="gpt-3.5-turbo-0125"
    )
    return assistant
assistant = create_assistant(assistant_instructions)
print(assistant.id)

# Thread management
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)

def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id

# Generate response - add tool calling functionality
def generate_response(message_body, wa_id):

    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        thread = client.beta.threads.retrieve(thread_id)


    # Check for any existing active runs and only proceed if none are found
    runs = client.beta.threads.runs.list(thread_id=thread_id)
    
    # Check if any run is in the specified statuses
    for run in runs.data:
        if run.status is not ["queued", "in_progress", "requires_action", "cancelling"]:
             # Add message to thread 
            message = client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message_body,
            )

    # Run the assistant and get the new message
    new_message = run_assistant(thread, wa_id)
    return new_message

def run_assistant(thread, wa_id, run=None):
    # Define an initial run if not provided
    if run is None:
        # Retrieve the Assistant
        assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

        # Start a new run
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
    
    #Implement run check count
    run_check_count = 0

  
        # Wait for completion
    while run.status != "completed":
        run_check_count += 1
        if run_check_count < 6:

            #Check if the run requires action and the action is to submit tool outputs
            if run.status == 'requires_action' and run.required_action.type == 'submit_tool_outputs':
                create_tool_outputs(run, wa_id)

            # Be nice to the API
            time.sleep(10)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        else:
            delete_existing_runs(thread.id)
            return "We had an issue processing your message. Submit it again."

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    return new_message

def create_tool_outputs(run, wa_id):

    # Extract single tool call
    tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    print(f"Function Name: {name}")
    print(f"Function Arguments: {arguments}")

    # Pull credentials and document_id from database with wa_id
    credentials = get_user_credentials(wa_id)
    document_id = get_most_recent_document(wa_id)['document_id']

    responses = batch_update_google_docs_document(credentials, document_id, arguments["update_requests"])

    # Submit the tool outputs for the given thread ID and run ID
    # Note: Adjust the tool_outputs list as per your specific requirements
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=run.thread_id,
        run_id=run.id,
        tool_outputs=[
            {
                "tool_call_id": tool_call.id,
                "output": json.dumps(responses)
            },
        ]
    )
