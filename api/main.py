from enum import Enum
import json
from typing import Optional
from flask import request
from flask import Flask, jsonify
import os
import random

import requests

from dotenv import load_dotenv  # type: ignore

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

    def get_by_name(name) -> Optional[str]:
        for deck in DeckIds:
            if deck.name == name:
                return deck.value
        return None


@app.route("/api/cards", methods=["POST"])
def create_card():
    data = json.loads(request.get_data(as_text=True))
    deck_id = DeckIds.get_by_name(data.get("deck"))
    if deck_id is None:
        return jsonify({"error": "Invalid deck"}), 400

    mochi_data = {"content": data.get("front") + "\n---\n" + data.get("back"), "deck-id": deck_id}
    response = requests.post("https://app.mochi.cards/api/cards", json=mochi_data, auth=(os.getenv("MOCHI_API_KEY"), ""))

    if response.status_code not in [201, 200]:
        return jsonify({"error": response.text}), 500
    return jsonify({"response": response.text}), 200


@app.route("/api/card", methods=["GET"])
def get_card():
    data = json.loads(request.get_data(as_text=True))
    response = requests.get(f"https://app.mochi.cards/api/cards/{data['card_id']}", auth=(os.getenv("MOCHI_API_KEY"), ""))

    if response.status_code not in [201, 200]:
        return jsonify({"error": response.text}), 500
    return jsonify({"response": response.text}), 200


@app.route("/api/card", methods=["PUT"])
def update_card():
    data = json.loads(request.get_data(as_text=True))
    mochi_data = {"content": data.get("front") + "\n---\n" + data.get("back")}
    response = requests.post(
        f"https://app.mochi.cards/api/cards/{data['card_id']}", json=mochi_data, auth=(os.getenv("MOCHI_API_KEY"), "")
    )

    if response.status_code not in [201, 200]:
        return jsonify({"error": response.text}), 500
    return jsonify({"response": response.text}), 200


@app.route("/api/card/delete", methods=["POST"])
def delete_card():
    data = json.loads(request.get_data(as_text=True))
    response = requests.delete(f"https://app.mochi.cards/api/cards/{data['card_id']}", auth=(os.getenv("MOCHI_API_KEY"), ""))
    print(response.text)

    if response.status_code not in [201, 200]:
        return jsonify({"error": response.text}), 500
    return jsonify({"response": response.text}), 200


@app.route("/api/privacy", methods=["GET"])
def privacy_policy():
    return open("static/privacy-policy.txt", "r").read()


@app.route("/api/openai-schema.yaml", methods=["GET"])
def openai_schema():
    return open("static/openai-schema.yaml", "r").read()


if __name__ == "__main__":
    app.run(debug=True)
