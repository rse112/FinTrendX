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


def is_recent(pub_date_str, start_day=-1, end_day=-9):
    pub_date = dateutil.parser.parse(pub_date_str)
    start_date = datetime.now() + timedelta(days=start_day)
    end_date = datetime.now() + timedelta(days=end_day)
    return start_date >= pub_date >= end_date


async def fetch_blog_data(
    session, client_id, client_secret, query, start, output_file, retries=6
):
    base_url = "https://openapi.naver.com/v1/search/blog"
    params = f"?query={quote(query)}&display=100&start={start}&sort=date"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}

    for attempt in range(retries):
        try:
            async with session.get(base_url + params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    post_dates = [item["postdate"] for item in data["items"]]
                    return data
                else:
                    pass
        except Exception as e:
            print(f"Request exception: {e}, attempt {attempt+1} of {retries}")

        await asyncio.sleep(2 * attempt)
    return None


async def fetch_all_blog_data_for_keyword(
    session, client_id, client_secret, query, output_file
):
    all_items = []

    for start in range(1, 1001, 100):
        data = await fetch_blog_data(
            session, client_id, client_secret, query, start, output_file
        )
        if data:
            valid_items = [
                item for item in data["items"] if is_recent(item["postdate"])
            ]
            all_items.extend(valid_items)

    # 모든 데이터를 모았으면 한꺼번에 파일에 저장
    post_dates = [item["postdate"] for item in all_items]

    return all_items


async def process_keyword_chunk(
    session, client_id, client_secret, keywords_chunk, output_file
):

    for query in keywords_chunk:
        results = await fetch_all_blog_data_for_keyword(
            session, client_id, client_secret, query, output_file
        )
        print(f"Processed {len(results)} items for keyword: '{query}'")
        await asyncio.sleep(0.1)


async def process_partition(partition, client_id, client_secret, output_file):

    async with aiohttp.ClientSession() as session:
        keyword_chunks = list(divide_chunks(partition, 1))
        for chunk in keyword_chunks:
            await process_keyword_chunk(
                session, client_id, client_secret, chunk, output_file
            )


def divide_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def main(keywords, clients):
    output_file = "blog_data.json"  # 여기서 직접 설정
    total_keywords = len(keywords)
    total_clients = len(clients)
    keywords_per_client = (
        total_keywords // total_clients
    )  # 각 클라이언트당 처리할 키워드 개수
    remainder = total_keywords % total_clients  # 남은 키워드 개수

    start_index = 0
    end_index = 0
    tasks = []

    for i, client in enumerate(clients):
        end_index += keywords_per_client
        if i < remainder:
            end_index += 1  # 남은 키워드를 분배

        partition = keywords[start_index:end_index]
        start_index = end_index

        tasks.append(
            process_partition(partition, client["id"], client["secret"], output_file)
        )

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

today = datetime.now().strftime("%y%m%d")
target_keywords = load_list_from_text(
    f"./data/target_keywords/{today}/target_keywords.txt"
)
# target_keywords = [
#     "월세지원금",
#     "해외선물",
#     "금ETF",
#     "일자리사이트",
#     "재택근무직업",
#     "한미반도체주가",
#     "AMD주가",
#     "하이닉스주가",
# ]
output_file = "blog_data.json"  # 파일명을 원하는 대로 수정하세요

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start = time()
    try:
        loop.run_until_complete(main(target_keywords, clients))
    finally:
        end = time()
        print(end - start)
