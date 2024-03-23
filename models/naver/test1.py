import aiohttp
import asyncio
import json
from urllib.parse import quote
import sys
from datetime import datetime, timedelta
import dateutil.parser

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from time import time


def is_recent(pub_date_str, start_day=-1, end_day=-8):
    pub_date = dateutil.parser.parse(pub_date_str)
    start_date = datetime.now() + timedelta(days=start_day)
    end_date = datetime.now() + timedelta(days=end_day)
    return start_date >= pub_date >= end_date


async def fetch_blog_data(session, client_id, client_secret, query, start, retries=6):

    base_url = "https://openapi.naver.com/v1/search/blog"
    params = f"?query={quote(query)}&display=100&start={start}&sort=date"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}

    for attempt in range(retries):
        try:
            async with session.get(base_url + params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    # print(
                    #     f"Request failed with status {response.status}, attempt {attempt+1} of {retries}"
                    # )
                    pass
        except Exception as e:
            print(f"Request exception: {e}, attempt {attempt+1} of {retries}")

        await asyncio.sleep(2 * attempt)
    recent_items = [item for item in data["items"] if is_recent(item["pubDate"])]
    return {"items": data["items"], "recent_count": len(recent_items)}


async def process_keyword_chunk(session, client_id, client_secret, keywords_chunk):

    for query in keywords_chunk:
        results = await fetch_all_blog_data_for_keyword(
            session, client_id, client_secret, query
        )
        print(
            f"Processed {len(results['items'])} items for keyword: '{query}', recent: {results['recent_count']}"
        )
        await asyncio.sleep(0.1)


async def fetch_all_blog_data_for_keyword(session, client_id, client_secret, query):

    tasks = [
        fetch_blog_data(session, client_id, client_secret, query, start)
        for start in range(1, 1001, 100)
    ]
    results = await asyncio.gather(*tasks)
    all_items = [item for result in results if result for item in result["items"]]

    return all_items


async def process_partition(partition, client_id, client_secret):

    async with aiohttp.ClientSession() as session:
        keyword_chunks = list(divide_chunks(partition, 1))
        for chunk in keyword_chunks:
            await process_keyword_chunk(session, client_id, client_secret, chunk)


def divide_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def main(keywords, clients):

    partitions = list(divide_chunks(keywords, len(keywords) // len(clients)))
    tasks = [
        process_partition(partitions[i], clients[i]["id"], clients[i]["secret"])
        for i in range(len(clients))
    ]
    await asyncio.gather(*tasks)


def load_list_from_text(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]


clients = [
    {"id": "TXYUStSiVj9St7tmCT5N", "secret": "k6bGRxUVJP"},
    {"id": "2J0Rhxh4Ig0SVFB3Oczm", "secret": "862RL1YrSm"},
    {"id": "e9PnkRRKvrJC_rg1rrD7", "secret": "_PctdaTXfD"},
    {"id": "MqeI5M7ymZsJix9plqtJ", "secret": "LRZWUFvL2S"},
    {"id": "PnrhTaVa2YQ8ZKnaLg9G", "secret": "fQePz5kBbI"},
    {"id": "KQm2sCylAtLmaJhusb7w", "secret": "D_ntjREaMT"},
]
today = today = datetime.now().strftime("%y%m%d")
target_keywords = load_list_from_text(
    f"./data/target_keywords/{today}/target_keywords.txt"
)


if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start = time()
    try:
        loop.run_until_complete(main(target_keywords, clients))
    finally:
        end = time()
        print(end - start)
