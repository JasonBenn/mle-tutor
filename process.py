import aiohttp
from dataclasses import dataclass
import asyncio
from functools import partial
import os
from typing import AsyncGenerator
from bs4 import BeautifulSoup
from openai import OpenAI
import glob
import re

client = OpenAI()
MODEL = "gpt-4o"
MAX_TOKENS = 128000


def summarize_text(text):
    # ipdb.set_trace()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are the world's best professor for senior machine learning engineers. You create expert summaries of advanced content. Your summaries are full of practical insights with thoughtful quiz questions interspersed throughout.",
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )
    return response.choices[0].message.content


@dataclass
class Scrapeable:
    url: str
    page_title: str
    filename: str
    scraped: bool


async def with_semaphore(semaphore, function):
    async with semaphore:
        await function()


async def scrape(task: Scrapeable):
    print(f"scraping {task.url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(task.url) as response:
            text = await response.text()
            # await asyncio.sleep(1)

    soup = BeautifulSoup(text, "html.parser")
    parsed_text = soup.get_text()
    with open(task.filename, "w") as f:
        f.write(parsed_text)


async def new_urls() -> AsyncGenerator[Scrapeable, None]:
    for file_path in glob.glob("urls/*"):
        with open(file_path, "r") as file:
            content = file.read()
            for line in content.strip().split("\n"):
                if re.search(r"https?://", line):
                    url = re.search(r"https?://\S+", line).group(0).strip()
                else:
                    continue
                title = re.sub(r"\W+", "-", re.sub(r"^https?://", "", url)).strip("-")
                title, url = title.strip(), url.strip()
                formatted_title = re.sub(r"\W+", "-", title[:50]).lower()
                filename = "scraped/" + formatted_title + ".txt"
                yield Scrapeable(url=url, page_title=title, filename=filename, scraped=os.path.exists(filename))


async def main():
    semaphore = asyncio.Semaphore(3)
    tasks = []
    async for task in new_urls():
        if not task.scraped:
            tasks.append(asyncio.create_task(with_semaphore(semaphore, partial(scrape, task))))
    await asyncio.gather(*tasks)
    print("done")


asyncio.run(main())
