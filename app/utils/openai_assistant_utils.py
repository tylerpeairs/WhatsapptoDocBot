from openai import OpenAI
from dotenv import load_dotenv
import logging
import os
import time
import json
from app.database import store_thread, get_most_recent_document, get_user_credentials, check_if_thread_exists
from .google_doc_utils import batch_update_google_docs_document

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPEN_AI_API_KEY)




# Generate a 10 edge and test cases

# --------------------------------------------------------------
# Generate response
# --------------------------------------------------------------
def generate_response(message_body, wa_id, document_content, credentials):
 

    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)
    print(f"Thread ID: {thread_id}")


    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        thread = client.beta.threads.retrieve(thread_id)
        print(f"Thread Retrieved: {thread}")

    # Ensure all previous runs are deleted/cancelled before proceeding
    delete_existing_runs(thread_id)

    # Check for any existing active runs and only proceed if none are found
    if not check_for_active_runs(thread_id):
        # Prepare the structured message content
        whatsapp_text = message_body
        content_to_send = {
            "whatsapp_text": whatsapp_text,
            "document_content": document_content
        }

        # Add message to thread
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=json.dumps(content_to_send) 
        )

        # Run the assistant and get the new message
        new_message = run_assistant(thread, wa_id)
        print(f"To wa_id:", new_message)
        return new_message
    else:
        print("Active run detected. Waiting for completion before proceeding.")
        return "Processing previous request. Please wait."


# --------------------------------------------------------------
# Run assistant
# --------------------------------------------------------------
def run_assistant(thread, wa_id):
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
            create_tool_outputs(run, wa_id)

        # Be nice to the API
        time.sleep(10)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        


    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    return new_message



def create_tool_outputs(run, wa_id):
    # Extract the first tool call ID from the required actions

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


# Check if there are any active runs for the thread
def check_for_active_runs(thread_id):
    # Retrieve all runs for the thread
    runs = client.beta.threads.runs.list(thread_id=thread_id)
    # Check if any run is in progress, requires action, or is queued
    for run in runs.data:
        if run.status in ["in_progress", "requires_action", "queued", "cancelling"]:
            return True  # An active run exists
    return False  # No active runs
            
# Delete any existing runs for the thread
def delete_existing_runs(thread_id):
    # Retrieve all runs for the thread
    runs = client.beta.threads.runs.list(thread_id=thread_id)
    for run in runs.data:
        # Check if the run is in a state that allows for cancellation
        if run.status in ["in_progress", "requires_action", "queued", "cancelling"]:
            print(f"Cancelling run: {run.id} with status: {run.status}")
            try:
                # Attempt to cancel the run
                cancelled_run = client.beta.threads.runs.cancel(
                    thread_id=thread_id,
                    run_id=run.id
                )
                print(f"Successfully cancelled run: {run.id}")
            except Exception as e:
                print(f"Error cancelling run {run.id}: {str(e)}")
