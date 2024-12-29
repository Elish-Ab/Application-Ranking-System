from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Step 1: Define candidate filtering questions
questions = [
    "What is your area of expertise?",
    "How many years of experience do you have in this field?",
    "Are you available for full-time work?"
]

# Step 2: Define responses to store candidate answers
responses = {
    "expertise": None,
    "experience": None,
    "availability": None,
}

@app.route("/bot", methods=["POST"])
def bot():
    # Get the incoming message from WhatsApp
    incoming_msg = request.values.get("Body", "").lower()
    response = MessagingResponse()
    msg = response.message()

    # Step 3: Ask the first question if the candidate hasn't answered it
    if responses["expertise"] is None:
        responses["expertise"] = incoming_msg
        msg.body(questions[1])  # Move to next question: experience
    # Step 4: Ask the second question if the candidate has answered the first
    elif responses["experience"] is None:
        responses["experience"] = incoming_msg
        msg.body(questions[2])  # Move to next question: availability
    # Step 5: Ask the third question if the candidate has answered the first two
    elif responses["availability"] is None:
        responses["availability"] = incoming_msg
        msg.body(f"Thank you! We have received your responses. We will review your application.")
        
        # Step 6: Filter based on answers and send appropriate response
        if int(responses["experience"]) < 2:
            msg.body("Unfortunately, your experience does not meet the required criteria for this position.")
        elif responses["availability"].lower() != "yes":
            msg.body("We are currently only looking for full-time candidates.")
        else:
            msg.body("Your profile matches our requirements. You will be contacted soon.")

        # Reset the responses for the next candidate
        responses["expertise"] = None
        responses["experience"] = None
        responses["availability"] = None

    return str(response)


if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
