import aiohttp
import pandas as pd
import json
import asyncio
import sys
import os
import time
import requests
# 현재 파일의 디렉토리를 구함
current_dir = os.path.dirname(os.path.abspath(__file__))

# 현재 디렉토리의 상위 디렉토리를 구함
parent_dir = os.path.dirname(current_dir)

# 상위 디렉토리(def_new_project)를 모듈 검색 경로에 추가
sys.path.append(parent_dir)

# 이제 상위 디렉토리에 있는 utils 모듈을 임포트할 수 있음
import utils

async def fetch_blog(client_id, client_secret, query, display, start, sort):
    encText = aiohttp.helpers.quote(query)
    url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display={display}&start={start}&sort={sort}"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_body = await response.read()
                response_json = json.loads(response_body)
                return pd.DataFrame(response_json['items'])
            else:
                print("Error Code:", response.status)
                return pd.DataFrame()
            


# 비동기 함수 실행을 위한 메인 함수
async def main():
    client_id = utils.get_secret("client_id")
    client_secret = utils.get_secret("client_secret")
    query = "검색어"
    display = 100
    start = 1
    sort = "sim"

    blog_df = await fetch_blog(client_id, client_secret, query, display, start, sort)
    print(blog_df)


def blog_sync(client_id, client_secret, query, display, start, sort):
    encText = requests.utils.quote(query)
    url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display={display}&start={start}&sort={sort}"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        return pd.DataFrame(response_json['items'])
    else:
        print("Error Code:", response.status_code)
        return pd.DataFrame()

# 동기적 실행을 위한 메인 함수
def main_sync():
    client_id = utils.get_secret("client_id")
    client_secret = utils.get_secret("client_secret")
    query = "검색어"
    display = 1000
    start = 1
    sort = "sim"
    
    start_time = time.time()
    blog_df = blog_sync(client_id, client_secret, query, display, start, sort)
    print(blog_df)
    print("동기적 실행 시간:", time.time() - start_time)

# if __name__ == "__main__":
#     main_sync()
# if __name__ == "__main__":
#     start=time.time()
#     asyncio.run(main())
#     print(time.time()-start)