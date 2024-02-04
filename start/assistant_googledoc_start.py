from multiprocessing import context
from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
from datetime import datetime
from app.database import get_user_credentials


load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

action_schema = {
  "openapi": "3.1.0",
  "info": {
    "title": "Google Docs API Services",
    "description": "Interact with the Google Docs API to create and manage documents.",
    "version": "v1.0.0"
  },
  "servers": [
    {
      "url": "https://docs.googleapis.com/v1"
    }
  ],
  "paths": {
    "/documents": {
      "post": {
        "description": "Create a new Google Doc with a specified title",
        "operationId": "CreateDocument",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "title": {
                    "type": "string",
                    "description": "Title of the document to be created"
                  }
                },
                "required": ["title"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Document created successfully",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "documentId": {
                      "type": "string",
                      "description": "The ID of the created document"
                    },
                    "title": {
                      "type": "string",
                      "description": "The title of the created document"
                    }
                  }
                }
              }
            }
          }
        },
        "security": [
          {
            "bearerAuth": []
          }
        ]
      }
    }
  },
  "components": {
    "securitySchemes": {
      "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
      }
    }
  }
}



# --------------------------------------------------------------
# Create assistant
# --------------------------------------------------------------
def create_assistant(access_token):

    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp Google Doc Assistant",
        instructions="You're a helpful WhatsApp assistant that can assist guests that are staying in our Paris AirBnb. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
        tools=[
            {
                "type": "function",
                "function": action_schema
            }
        model="gpt-4-1106-preview"
    )
    return assistant


assistant = create_assistant()


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
