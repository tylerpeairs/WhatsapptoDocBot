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

def getTools(array):
  # call this function to get your template json to attache to a new Assistant.
  # the array contains the function NAMES only
  # tool = getTools(["getContact", "webscrape"])

    tools = []
    l = globals()
    for a in array:
        f = None
        try:
            f = l[a]
        except:
            pass
        if f!=None:
            tools.append( {"type": "function","function" : f()})
    return tools

tools = getTools(["batch_update_google_docs_document"])


# --------------------------------------------------------------
# Create assistant
# --------------------------------------------------------------
def create_assistant(assistant_instructions, tools):

    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp Google Doc Assistant",
        instructions=assistant_instructions,
        tools=tools,
        model="gpt-4-1106-preview"
    )
    return assistant


assistant = create_assistant(assistant_instructions, tools)
print(assistant)

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
def generate_response(message_body, wa_id, name, document_title, access_token):
 

    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        print(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        print(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    structured_message_content = {
        "body": message_body,  # Original message body
        "context": {
            "documentTitle": document_title,
            "accessToken": access_token  # Be cautious with passing sensitive information
        }
    }
    
    # Convert structured_message_content to a string if necessary
    # Ensure your system handles this securely
    content_to_send = json.dumps(structured_message_content)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content_to_send, 
    )

    # Run the assistant and get the new message
    new_message = run_assistant(thread)
    print(f"To {name}:", new_message)
    return new_message


# --------------------------------------------------------------
# Run assistant
# --------------------------------------------------------------
def run_assistant(thread):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve("asst_iokYs2cFrRtJ9T3ugMPxaDwV")

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

#new_message = generate_response("What's the check in time?", "123", "John")

#new_message = generate_response("What's the pin for the lockbox?", "456", "Sarah")

#new_message = generate_response("What was my previous question?", "123", "John")

#new_message = generate_response("What was my previous question?", "456", "Sarah")



"""You're a helpful WhatsApp assistant that assists businesses in organizing their WhatsApp messages by inputing them into a Google Document and categorizing them. Use the provided Google Docs API function batch_update_google_docs_document and update the document according to the user's whatsapp message.

You will receive 3 variables:: 

2. whatsapp_text is the text content from the user's most recent whatsapp message. This is the text which will be added to the document.
3. document_content is the JSON object returned from Google's get document API which will need to be manipulated to insert the whatsapp_text in an organized and categorized format. You must extract the document_id from this and use it as part of your batch_update request.
4. user credentials is the credentials needed to post the batch update request

Here are the values for these 4 variables:
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

You will change the text to be more readable, so you might change it to "Received 300 pesos from Tyler", and you could categorize it under "Money Received". Then you make a corresponding batch update request where you input the new text under the Money Received categorization by using the batch_update_google_docs_document function. If there is existing text in the document_content, you must use that text as context, so you may not always need to create new categories but instead can add text under an existing category. Additionally, you will not always categorize or add text at the beginning or the end of the document. Rather, read the document_content object and decide the most logical place to insert the new text and categories.

Your response may look like:
Google Docs Link: https://docs.google.com/document/d/example_document_id/edit
Categorized: "Money Received"
Text Added: "Received 300 pesos from Tyler"
"""


# Create tools array to input into the assistants API from our utils functions
    


"""
def callTools(tool_calls):
# the parameter comes straight from the openAI run 
    tool_outputs = []
    for t in tool_calls:
        functionName = t.function.name
        attributes = json.loads(t.function.arguments)
        try:
            functionResponse =globals()[functionName](attributes)
        except:
             # we just tell openAi we couldn't :)
            functionResponse = { "status" : 'Error in function call '+functionName+'('+t.function.arguments+')' }
        tool_outputs.append(  { "tool_call_id": t.id , "output": json.dumps(functionResponse) })
    return tool_outputs
"""