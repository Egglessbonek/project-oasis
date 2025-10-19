# =============================================================================
#                  Project Oasis - Flask Backend (app.py)
#
# This is the main entry point for our Flask application.
#
# We are now fixing the database health check to use the modern
# SQLAlchemy 2.0 syntax.
#
# =============================================================================

import os
from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv
from sqlalchemy import text # <-- IMPORT THE text() CONSTRUCT

# Import the db object and the new Blueprint
from project.database import db
from project.routes import api_bp

# Load environment variables from .env file
load_dotenv()

# Create the Flask application object
app = Flask(__name__)

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the .env file")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- Initialize Extensions ---
db.init_app(app)

# --- Register Blueprints ---
app.register_blueprint(api_bp)


@app.route("/")
def index():
    """A simple endpoint to welcome users to the API."""
    return jsonify({"message": "Welcome to the Project Oasis API!"})

@app.route("/api/ping")
def ping():
    """A simple health-check endpoint to verify the server is responsive."""
    try:
        # Wrap the raw SQL string in the text() construct
        db.session.execute(text('SELECT 1')) # <-- APPLY THE FIX HERE
        return jsonify({"status": "ok", "message": "pong"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Database connection failed", "error": str(e)}), 500

@app.route("/sms", methods=['POST'])
def sms_reply():
    # Get the message data from the incoming request
    # Twilio sends this as form data
    sender_number = request.form.get('From')
    message_body = request.form.get('Body')

    # Check if there is an image (for your project)
    # Twilio sends media in fields like 'MediaUrl0', 'MediaUrl1', etc.
    image_url = request.form.get('MediaUrl0')

    # --- This is where your project logic goes! ---
    # For now, just print it to your terminal
    print(f"--- NEW REPORT from {sender_number} ---")
    print(f"Message: {message_body}")

    if image_url:
        print(f"Image URL: {image_url}")
    else:
        print("No image attached.")
    print("------------------------------------------")
    # -----------------------------------------------

    # Respond to Twilio to let it know you received the message
    # We can send an empty response
    return Response(status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

