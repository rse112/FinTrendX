import aiohttp
import asyncio
import json
from urllib.parse import quote
import sys
from datetime import datetime, timedelta
import dateutil.parser
import pandas as pd

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
    return all_items


async def process_keyword_chunk(
    session, client_id, client_secret, keywords_chunk, output_file
):
    results = []
    for query in keywords_chunk:
        result = await fetch_all_blog_data_for_keyword(
            session, client_id, client_secret, query, output_file
        )
        results.append(result)
        print(f"Processed {len(result)} items for keyword: '{query}'")
        await asyncio.sleep(0.1)
    return results


async def process_partition(partition, client_id, client_secret, output_file):
    async with aiohttp.ClientSession() as session:
        keyword_chunks = list(divide_chunks(partition, 1))
        results = []
        for chunk in keyword_chunks:
            result = await process_keyword_chunk(
                session, client_id, client_secret, chunk, output_file
            )
            results.extend(result)
        return results


def divide_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def main_blog(keywords, clients):
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
    results = await asyncio.gather(*tasks)
    # 결과를 DataFrame으로 변환
    df = pd.DataFrame()
    for result in results:
        for keyword_data in result:
            df = pd.concat([df, pd.DataFrame([len(keyword_data)])], ignore_index=True)

    return df


def load_list_from_text(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]


clients = [
    {"id": "DSTJ9BxDk6_K36vAFdPC", "secret": "0UzqagaL2q"},
    {"id": "e_s2bR7O0YYpfUe7HGZp", "secret": "2B9777BzQq"},
    {"id": "ab3xh3cd6CqsZAATQ67J", "secret": "Bi6JlDK9lY"},
    {"id": "Wt3zwLX11pd9nQcHV8Bi", "secret": "Ecg09WFoLl"},
    {"id": "q_8iSvgm0YYZlmydrdkE", "secret": "8AFxQr8d5f"},
    {"id": "OADb6YuUPVceLPI6GKJx", "secret": "THnY1yNehk"},
]

today = datetime.now().strftime("%y%m%d")
target_keywords = load_list_from_text(
    f"./data/target_keywords/{today}/target_keywords.txt"
)


def process_and_save_df(df, target_keywords, today):
    # DataFrame에 키워드 열 추가
    df["keyword"] = target_keywords

    # 열 이름 변경
    df = df.rename(columns={0: "Activity_Rate"})

    # 활동률 계산 및 반올림
    df["Activity_Rate"] = round(df["Activity_Rate"] / 10, 3)

    # 열 재정렬
    df = df.reindex(
        columns=["keyword"] + [col for col in df.columns if col != "keyword"]
    )

    # CSV 파일로 저장
    save_path = f"./data/target_keywords/{today}/keyword_activity_rates.csv"
    df.to_csv(save_path, index=False)

    return df


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start = time()
    try:
        df = loop.run_until_complete(main_blog(target_keywords, clients))
        # 변경된 부분: 아래 코드를 process_and_save_df 함수 호출로 대체합니다.
        df = process_and_save_df(df, target_keywords, today)
    finally:
        end = time()
        print(f"Total time: {end - start}")
    print(df)
