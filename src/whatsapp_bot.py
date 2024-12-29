import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

app = Flask(__name__)

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Open the Google Sheet by name
sheet = client.open("Job Applications").sheet1

# Define candidate filtering questions
questions = [
    "What is your area of expertise?",
    "How many years of experience do you have working directly with B2B clients?",
    "Do you have experience in direct sales?",
    "Do you have administrative experience?",
    "Are you available for a full-time position?"
]

# Define user session data
user_sessions = {}

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").lower()
    from_number = request.values.get("From")  # Unique identifier for the user
    response = MessagingResponse()
    msg = response.message()

    # Initialize user session if it doesn't exist
    if from_number not in user_sessions:
        user_sessions[from_number] = {
            "step": 0,
            "responses": {}
        }

    user_data = user_sessions[from_number]

    # Handle the /start command
    if incoming_msg == "/start":
        msg.body("Welcome to the Job Application Bot! Please answer a few questions to help us evaluate your application. Let's get started!\n\n" + questions[0])
        user_data["step"] = 1  # Start the question flow
        return str(response)

    # Handle the question flow
    step = user_data["step"]

    if step > 0 and step <= len(questions):
        # Save the user's response for the current question
        user_data["responses"][f"q{step}"] = incoming_msg

        # Check if there are more questions to ask
        if step < len(questions):
            msg.body(questions[step])  # Ask the next question
            user_data["step"] += 1
        else:
            # All questions answered, thank the user and save responses
            msg.body("Thank you! We have received your responses. We will review your application.")

            # Save responses to Google Sheets
            sheet.append_row([
                str(datetime.datetime.now()),  # Timestamp
                user_data["responses"].get("q1", ""),
                user_data["responses"].get("q2", ""),
                user_data["responses"].get("q3", ""),
                user_data["responses"].get("q4", ""),
                user_data["responses"].get("q5", "")
            ])

            # Reset user session
            user_sessions[from_number] = {"step": 0, "responses": {}}
    else:
        # If the user sends a message without starting the process
        msg.body("Please type /start to begin your application process.")

    return str(response)


if __name__ == "__main__":
    app.run(debug=True)
