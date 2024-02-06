from openai import OpenAI
from dotenv import load_dotenv
import logging
import os
import time
import json
from app.database import store_thread, get_most_recent_document, get_user_credentials, check_if_thread_exists, update_token_usage
from .google_doc_utils import batch_update_google_docs_document
import shelve
from app import create_app

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPEN_AI_API_KEY)


test = True  # Set to True to generate test cases

# Generate a 10 edge and test cases
if test is False:
    # Generate response
    def generate_response(message_body, wa_id, document_content):
    

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

        existing_run = check_for_active_runs(thread_id)

        # Check for any existing active runs and only proceed if none are found
        if existing_run is None:
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
            new_message = run_assistant(thread, wa_id, run)
            return "Processing previous request. Please wait and resubmit your message after." #TODO: queing message

    # Run assistant
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
                print("Run check count exceeded. Deleting all runs.")
                delete_existing_runs(thread.id)
                return "We had an issue processing your message. Submit it again."

        # Update the total token usage for the user
        total_token_usage = run.usage.total_tokens
        update_token_usage(wa_id, int(total_token_usage))
        logging.info(f"Total token usage for user {wa_id}: {total_token_usage}")

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
            if run.status in ["requires_action"]:
                return run
        return None  # No active runs
                
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

else:
        # Thread management
    def check_if_thread_exists(wa_id):
        with shelve.open("threads_db") as threads_shelf:
            return threads_shelf.get(wa_id, None)

    def store_thread(wa_id, thread_id):
        with shelve.open("threads_db", writeback=True) as threads_shelf:
            threads_shelf[wa_id] = thread_id

    # Generate response - add tool calling functionality
    def generate_response(message_body, wa_id, document_content):
        thread = client.beta.threads.create()
        thread_id = thread.id

    
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
        new_update_requests = run_assistant(thread, wa_id)
        return new_update_requests

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
        

    
        # Wait for completion
        while run.status != "completed":
            #Check if the run requires action and the action is to submit tool outputs
            if run.status == 'requires_action' and run.required_action.type == 'submit_tool_outputs':
                return get_tool_outputs(run, wa_id)
                          # Be nice to the API
            time.sleep(10)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)


    def get_tool_outputs(run, wa_id):

        # Extract single tool call
        tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
        name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Function Name: {name}")
        print(f"Function Arguments: {arguments}")
        raise Exception("Test stop: Function arguments printed.")


    # Test Cases
    #====================================

    # Define a custom exception for stopping a test case
    class TestCaseCompletedException(Exception):
        pass

    # Now you can safely call functions that require an application context
    message_body = {'object': 'whatsapp_business_account', 'entry': [{'id': '241544202367217', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15551294221', 'phone_number_id': '246316221888389'}, 'contacts': [{'profile': {'name': 'Tyler'}, 'wa_id': '12252781239'}], 'messages': [{'from': '12252781239', 'id': 'wamid.HBgLMTIyNTI3ODEyMzkVAgASGBYzRUIwQTgxMENENzNCQzg1RTFDMUZCAA==', 'timestamp': '1707173426', 'text': {'body': 'got 300 pesos Tyler'}, 'type': 'text'}]}, 'field': 'messages'}]}]}
    document_content = {'title': 'Whatsapp Notes 2024-02-05', 'body': {'content': [{'endIndex': 1, 'sectionBreak': {'sectionStyle': {'columnSeparatorStyle': 'NONE', 'contentDirection': 'LEFT_TO_RIGHT', 'sectionType': 'CONTINUOUS'}}}, {'startIndex': 1, 'endIndex': 2, 'paragraph': {'elements': [{'startIndex': 1, 'endIndex': 2, 'textRun': {'content': '\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}]}, 'documentStyle': {'background': {'color': {}}, 'pageNumberStart': 1, 'marginTop': {'magnitude': 72, 'unit': 'PT'}, 'marginBottom': {'magnitude': 72, 'unit': 'PT'}, 'marginRight': {'magnitude': 72, 'unit': 'PT'}, 'marginLeft': {'magnitude': 72, 'unit': 'PT'}, 'pageSize': {'height': {'magnitude': 792, 'unit': 'PT'}, 'width': {'magnitude': 612, 'unit': 'PT'}}, 'marginHeader': {'magnitude': 36, 'unit': 'PT'}, 'marginFooter': {'magnitude': 36, 'unit': 'PT'}, 'useCustomHeaderFooterMargins': True}, 'namedStyles': {'styles': [{'namedStyleType': 'NORMAL_TEXT', 'textStyle': {'bold': False, 'italic': False, 'underline': False, 'strikethrough': False, 'smallCaps': False, 'backgroundColor': {}, 'foregroundColor': {'color': {'rgbColor': {}}}, 'fontSize': {'magnitude': 11, 'unit': 'PT'}, 'weightedFontFamily': {'fontFamily': 'Arial', 'weight': 400}, 'baselineOffset': 'NONE'}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'alignment': 'START', 'lineSpacing': 115, 'direction': 'LEFT_TO_RIGHT', 'spacingMode': 'COLLAPSE_LISTS', 'spaceAbove': {'unit': 'PT'}, 'spaceBelow': {'unit': 'PT'}, 'borderBetween': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'borderTop': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'borderBottom': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'borderLeft': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'borderRight': {'color': {}, 'width': {'unit': 'PT'}, 'padding': {'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'indentFirstLine': {'unit': 'PT'}, 'indentStart': {'unit': 'PT'}, 'indentEnd': {'unit': 'PT'}, 'keepLinesTogether': False, 'keepWithNext': False, 'avoidWidowAndOrphan': True, 'shading': {'backgroundColor': {}}, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_1', 'textStyle': {'fontSize': {'magnitude': 20, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 20, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 6, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_2', 'textStyle': {'bold': False, 'fontSize': {'magnitude': 16, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 18, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 6, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_3', 'textStyle': {'bold': False, 'foregroundColor': {'color': {'rgbColor': {'red': 0.2627451, 'green': 0.2627451, 'blue': 0.2627451}}}, 'fontSize': {'magnitude': 14, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 16, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_4', 'textStyle': {'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}}, 'fontSize': {'magnitude': 12, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 14, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_5', 'textStyle': {'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}}, 'fontSize': {'magnitude': 11, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 12, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'HEADING_6', 'textStyle': {'italic': True, 'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}}, 'fontSize': {'magnitude': 11, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'magnitude': 12, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'TITLE', 'textStyle': {'fontSize': {'magnitude': 26, 'unit': 'PT'}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'unit': 'PT'}, 'spaceBelow': {'magnitude': 3, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}, {'namedStyleType': 'SUBTITLE', 'textStyle': {'italic': False, 'foregroundColor': {'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}}, 'fontSize': {'magnitude': 15, 'unit': 'PT'}, 'weightedFontFamily': {'fontFamily': 'Arial', 'weight': 400}}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT', 'spaceAbove': {'unit': 'PT'}, 'spaceBelow': {'magnitude': 16, 'unit': 'PT'}, 'keepLinesTogether': True, 'keepWithNext': True, 'pageBreakBefore': False}}]}, 'revisionId': 'ALBJ4Lsgh18wt6nmBGe_FTGoGIo7INvbZCnF1MJqdoRaKErclOmgf5IChNAcK92-GoGhTYEoKcpaCSdjgZvpgA', 'suggestionsViewMode': 'SUGGESTIONS_INLINE', 'documentId': '1_5V0t_R44fHQej32k4fSCmtjclaK2H-jz8KlIQbFHs0'}
    test_cases = [
        {"message_body": message_body, "wa_id": "12252781239", "document_content": document_content},
        # Add more test cases as needed
    ]

    for case in test_cases:
        try:
            print(f"Starting test case: {case['message_body']}")
            response = generate_response(case["message_body"], case["wa_id"], case["document_content"])
        except TestCaseCompletedException as e:
            print(f"Test case stopped: {e}")
            continue  # Proceed to the next test case