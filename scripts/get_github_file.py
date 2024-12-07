import base64
import os
import requests

url = f"https://api.github.com/repos/JasonBenn/notes/contents/Periodic/Daily/2024-12-06.md"
response = requests.get(
    url,
    headers={
        "Authorization": f"Bearer {os.getenv('GITHUB_RW_NOTES_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept": "application/vnd.github+json",
    },
)
# print(url, response.json())
print(base64.b64decode(response.json()["content"]).decode("utf-8"))

