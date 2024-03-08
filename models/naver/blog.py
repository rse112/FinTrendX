import asyncio
import aiohttp
import json
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse

async def fetch_blog(session, url, headers):
    async with session.get(url, headers=headers) as response:
        rescode = response.status
        if rescode == 200:
            response_body = await response.text()
            response_json = json.loads(response_body)
            return pd.DataFrame(response_json['items'])
        else:
            print("Error Code:", rescode)
            return pd.DataFrame()

async def blog_async(client_id, client_secret, query, display, start, sort):
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display={str(display)}&start={str(start)}&sort={sort}"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    async with aiohttp.ClientSession() as session:
        return await fetch_blog(session, url, headers)

async def blog_result_async(types, std_time, client_id, client_secret):
    end_time = std_time - relativedelta(days=1)
    start_time = std_time - relativedelta(weeks=1) - relativedelta(days=1)
    end_time = end_time.strftime("%Y-%m-%d")
    start_time = start_time.strftime("%Y-%m-%d")

    display = 100
    sort = 'date'

    tasks = []
    for type_ in types:
        query = f'{type_}'
        for i in range(10):  # 10번 반복하여 총 1000개의 블로그 포스트 수집
            start = 1 + 100 * i
            tasks.append(blog_async(client_id, client_secret, query, display, start, sort))

    results = await asyncio.gather(*tasks)
    # 결과 처리 및 활동성 계산 로직을 여기에 구현

    return results  # 이 예제에서는 단순히 결과를 반환합니다.

if __name__ == "__main__":
    # 테스트를 위한 변수 정의
    client_id = "ByXmMvAqMIxyVUY_h17L"
    client_secret = "2x7yByvNSN"    
    types = ["비트코인", "파이썬"]  # 검색하고자 하는 키워드 목록
    std_time = datetime.now()  # 기준 시간 설정

    # 비동기 메인 함수 실행
    results = asyncio.run(blog_result_async(types, std_time, client_id, client_secret))
    
    # 결과 출력 (테스트 목적)
    print(results)
