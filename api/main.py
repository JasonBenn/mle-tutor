from bs4 import BeautifulSoup
import base64
from enum import Enum
import json
from utils import async_route, get_open_mics
from typing import Optional
import os
import random
from datetime import datetime
from flask import Flask, jsonify, request
import requests
import asyncio
import aiohttp

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
        text = get_random_slice("data/processed")
    else:
        text = get_random_slice("data/scraped")
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
    card_id = request.args.get("card_id")
    if not card_id:
        card_id = request.get_json().get("card_id")

    response = requests.get(f"https://app.mochi.cards/api/cards/{card_id}", auth=(os.getenv("MOCHI_API_KEY"), ""))

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


def get_github_file(path):
    response = requests.get(
        f"https://api.github.com/repos/JasonBenn/notes/contents/{path}",
        headers={
            "Authorization": f"Bearer {os.getenv('GITHUB_RW_NOTES_TOKEN')}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        },
    )
    return base64.b64decode(response.json()["content"]).decode("utf-8")


@app.route("/api/goals", methods=["GET"])
def goals():
    print("goals!")
    now = datetime.now()
    month = now.month
    quarter = (month - 1) // 3 + 1
    week = now.isocalendar()[1]
    year = now.year
    day = now.strftime("%Y-%m-%d")

    periods = request.json.get("periods", [])
    results = {}

    for period in periods:
        match period:
            case "day":
                path = f"Periodic/Daily/{day}.md"
            case "week":
                path = f"Periodic/Weekly/{year}-W{week}.md"
            case "month":
                path = f"Periodic/Monthly/{year}-{month:02d}.md"
            case "quarter":
                path = f"Periodic/Quarterly/{year}-Q{quarter}.md"
            case "year":
                path = f"Periodic/Annually/{year}.md"
            case _:
                return jsonify({"error": "Invalid period: should be any combination of [day, week, month, quarter, year]"}), 400

        results[period] = get_github_file(path)

    return jsonify({"results": results})


@app.route("/api/comedy", methods=["GET"])
@async_route
async def get_comedy_events():
    try:
        async with aiohttp.ClientSession() as session:

            async def fetch_and_parse(url):
                async with session.get(url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    return soup.get_text(strip=True, separator="\n")

            # Wrap the synchronous get_open_mics in an async function
            async def async_get_open_mics():
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, get_open_mics)

            open_mics_data, major_shows_data, small_shows_data = await asyncio.gather(
                async_get_open_mics(),
                fetch_and_parse("https://www.dead-frog.com/live-comedy/shows/94117/10"),
                fetch_and_parse("https://sf.funcheap.com/category/event/event-types/comedy-event-types-event/"),
            )

            return jsonify(
                {
                    "events": {
                        "open_mics": open_mics_data,
                        "major_shows": major_shows_data,
                        "small_shows": small_shows_data,
                    }
                }
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
