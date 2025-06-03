 # WhatsApp-to-Docs-AI

WhatsApp-to-Docs-AI is a Flask-based application that integrates with the WhatsApp Business Cloud API, OpenAI, and Google Docs to convert WhatsApp messages into clear, categorized entries in a Google Document. Incoming messages are processed via a webhook, rewritten and categorized by an AI model, and appended under the appropriate heading in a Google Doc in the user's Drive.

 ## Features
 - **Real-time Webhook Processing**: Receives WhatsApp messages via webhook and filters out status updates.
 - **AI-powered Rewriting & Categorization**: Uses OpenAI to rewrite messages for clarity and assign or create categories.
 - **Automated Google Docs Updates**: Creates and updates a Google Doc per user, inserting messages under category headings.
 - **Secure OAuth2 Storage**: Safely encrypts and stores user credentials and document metadata in a database.
 - **Extensible Flask Factory Structure**: Modular design with blueprints, decorators, and utilities.

 ## Table of Contents
 1. [Prerequisites](#prerequisites)
 2. [Installation](#installation)
 3. [Configuration](#configuration)
 4. [Usage](#usage)
    - [Running the Application](#running-the-application)
    - [Exposing via Ngrok](#exposing-via-ngrok)
    - [WhatsApp Webhook Setup](#whatsapp-webhook-setup)
    - [OAuth Flow](#oauth-flow)
 5. [Testing](#testing)
 6. [Project Structure](#project-structure)
 7. [Contributing](#contributing)
 8. [License](#license)

 ## Prerequisites
 - Python 3.8 or higher
 - pip (or pipenv/poetry)
 - A WhatsApp Business Cloud API phone number and access token
 - A Google Cloud project with OAuth2 credentials for the Docs API
 - An OpenAI API key
 - Ngrok (or another tunnel) for local webhook testing

 ## Installation

 1. Clone the repository:
    ```bash
    git clone https://github.com/your-org/WhatsapptoDocBot.git
    cd WhatsapptoDocBot
    ```
 2. (Optional) Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
 3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

 ## Configuration
 Create a `.env` file in the project root with the following variables:
 ```dotenv
 # WhatsApp / Facebook
 ACCESS_TOKEN=<your_whatsapp_access_token>
 APP_ID=<your_facebook_app_id>
 APP_SECRET=<your_facebook_app_secret>
 VERSION=<graph_api_version>
 PHONE_NUMBER_ID=<your_phone_number_id>
 VERIFY_TOKEN=<your_webhook_verify_token>

 # Flask & Database
 FLASK_SECRET_KEY=<your_flask_secret_key>
 SQLALCHEMY_DATABASE_URI=<your_database_uri>
 FERNET_KEY=<your_encryption_key>

 # Google OAuth2
 OAUTH_CLIENT_ID=<your_google_oauth_client_id>
 OAUTH_CLIENT_SECRET=<your_google_oauth_client_secret>
 NGROK_DOMAIN=<your_ngrok_subdomain>

 # OpenAI
 OPEN_AI_API_KEY=<your_openai_api_key>

 # Application Domain (used in links)
 APP_DOMAIN=https://<your_public_domain>
 ```

 Generate a Fernet key for `FERNET_KEY`:
 ```bash
 python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
 ```

 ## Usage

 ### Running the Application
 Start the Flask development server:
 ```bash
 python run.py
 ```

 ### Exposing via Ngrok
 To receive webhooks locally, expose port 8000:
 ```bash
 ngrok http 8000
 ```

 ### WhatsApp Webhook Setup
 Configure your webhook subscription following the [WhatsApp Cloud API docs](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks)
 using your `VERIFY_TOKEN` and the `https://<ngrok_subdomain>/webhook` callback URL.

 ### OAuth Flow
 Users must authorize the app to access their Google Docs:
 1. Send a WhatsApp message to trigger a login link.
 2. Follow the link to authenticate and grant the app permission.
 3. After successful login, messages will be added to the user’s Google Doc.

 ## Testing
 Run the full test suite:
 ```bash
 python tests/run_tests.py
 ```

 Use `watch_for_changes.py` to auto-run tests on file changes:
 ```bash
 python watch_for_changes.py
 ```

 ## Project Structure
 See [app/README.md](app/README.md) for details on the Flask application structure.

 Additional directories:
 - `prompt-engineering/`: experiments and resources for refining AI prompts.

 ## Contributing
 Contributions are welcome! Please open issues or pull requests for enhancements or bug fixes.

 ## License
 This project is licensed under the MIT License. See [LICENCE.txt](LICENCE.txt) for details.
