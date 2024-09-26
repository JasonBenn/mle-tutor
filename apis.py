from flask import Flask, jsonify
import os
import random

app = Flask(__name__)


def get_random_slice(directory, max_chars=5000):
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), "r") as file:
            text = file.read()
            start_index = random.randint(0, len(text) - max_chars)
            return text[start_index : start_index + max_chars]


@app.route("/api/random-text", methods=["GET"])
def random_text():
    text = get_random_slice("processed")
    return jsonify({"text": text})


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
