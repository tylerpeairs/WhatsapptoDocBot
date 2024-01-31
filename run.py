import logging

from app import create_app

# Create the Flask app
app = create_app()

if __name__ == "__main__":
    # Log a message indicating that the Flask app has started
    logging.info("Flask app started")

    # TODO: Turn debug off
    # Run the Flask app on host 0.0.0.0 and port 8000
    app.run(host="0.0.0.0", port=8000, debug=True)
