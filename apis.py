from enum import Enum
import json
from flask import request
from flask import Flask, jsonify
import os
import random

import requests

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)


def get_random_slice(directory, max_chars=5000):
    filename = random.choice(os.listdir(directory))
    with open(os.path.join(directory, filename), "r") as file:
        text = file.read()
        if len(text) <= max_chars:
            return text

        start_index = random.randint(0, len(text) - max_chars)
        return text[start_index : start_index + max_chars]


@app.route("/api/random-text", methods=["GET"])
def random_text():
    x = random.uniform(0, 1)
    if x < 0.6:
        text = get_random_slice("processed")
    else:
        text = get_random_slice("scraped")
    return jsonify({"text": text})


@app.route("/api/echo", methods=["GET", "POST"])
def echo():
    # Print entire HTTP request
    print("Request Method:", request.method)
    print("Request Headers:", request.headers)
    print("Request URL:", request.url)
    print("Request Body:", request.get_data(as_text=True))
    # Return a 201 status code
    return "", 201


class DeckIds(Enum):
    MACHINE_LEARNING = "rJvG6PtI"
    DISTRIBUTED_SYSTEMS = "dvQBuvKL"
    OPERATING_SYSTEMS = "7NCM3TQE"
    SYSTEM_DESIGN = "GOSfjUYP"
    PYTHON = "TWEo8eCJ"
    JAVASCRIPT = "vVo0I5hQ"
    NETWORKING = "PfIYqVVy"
    ARCHITECTURE = "MNDlT8v4"
    DATABASES = "jn4udgEj"
    PYTORCH = "cRm6jshY"


@app.route("/api/create-card", methods=["GET", "POST"])
def create_card():
    data = json.loads(request.get_data(as_text=True))
    if data.get("deck") not in [deck.name for deck in DeckIds]:
        return jsonify({"error": "Invalid deck"}), 400
    deck_id = DeckIds[data["deck"]].value

    mochi_data = {"content": data.get("front") + "\n---\n" + data.get("back"), "deck-id": deck_id}
    response = requests.post("https://app.mochi.cards/api/cards", json=mochi_data, auth=(os.getenv("MOCHI_API_KEY"), ""))

    print("Mochi API Response:", response.text)
    print("Mochi API Status Code:", response.status_code)

    if response.status_code not in [201, 200]:
        return jsonify({"error": "Failed to create card"}), 500
    return jsonify({"message": "Card created successfully"}), 201


@app.route("/api/privacy", methods=["GET"])
def privacy_policy():
    return """
    Privacy Policy for Random Text API

    Effective Date: 2024-09-25

    Introduction
    Welcome to the Random Text API! This privacy policy explains how we handle any data associated with the usage of our API.

    Data Collection
    The Random Text API does not collect or store any personally identifiable information (PII). Our API simply returns a randomly generated text, and no user input is required to use this service.

    Usage Data
    While using the Random Text API, we may collect anonymous usage statistics and server logs to monitor performance and ensure the reliability of our service. This information is non-identifiable and does not include any personal data.

    Third-Party Services
    Our API is hosted on Digital Ocean. They may collect anonymized data through server logs for operational purposes.

    Cookies
    This API does not use cookies or any tracking mechanisms.

    Data Security
    We use industry-standard security practices to protect the integrity and availability of the API. While we do not process sensitive personal information, we ensure that our systems are regularly updated and protected against security threats.

    Changes to this Privacy Policy
    We may update this privacy policy from time to time to reflect changes in our services or practices. Any updates will be posted on this page, and we encourage users to review it periodically.

    Contact Us
    If you have any questions about this privacy policy, please contact us at jasoncbenn@gmail.com.
    """


if __name__ == "__main__":
    app.run(debug=True)
