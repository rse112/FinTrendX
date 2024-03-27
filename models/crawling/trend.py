import sys
import os

# 현재 스크립트의 경로를 기준으로 상위 디렉토리의 절대 경로를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
import aiohttp
import asyncio
import pandas as pd
import json
from utils import get_secret
from datetime import datetime
from dateutil.relativedelta import relativedelta


async def fetch_data(session, url, headers, body):
    async with session.post(url, headers=headers, data=body) as response:
        try:
            response.raise_for_status()
            return await response.json()
        except aiohttp.ClientResponseError as e:
            # 예외 발생 시 URL 정보와 함께 커스텀 예외 메시지를 생성
            raise aiohttp.ClientResponseError(
                response.request_info,
                response.history,
                status=e.status,
                message=f"{e.message}, URL='{response.url}'",
            ) from e


def set_time_range(std_time, days_before=1, years_before=4):
    """
    기준 시간을 바탕으로 지정된 일수 전과 년수 전의 날짜를 계산하여 반환합니다.

        매개변수:
    - std_time: 기준이 되는 datetime 객체
    - days_before: 계산할 이전 일수 (기본값: 1일 전)
    - years_before: 계산할 이전 년수 (기본값: 4년 전)
    """
    end_time = (std_time - relativedelta(days=days_before)).strftime("%Y-%m-%d")
    start_time = (
        std_time - relativedelta(years=years_before, days=days_before)
    ).strftime("%Y-%m-%d")

    return start_time, end_time


async def trend_load_async(std_time, search_keyword, client_id, client_secret, url):
    start_time, end_time = set_time_range(std_time)
    data = {
        "startDate": start_time,
        "endDate": end_time,
        "timeUnit": "date",
        "keywordGroups": [{"groupName": search_keyword, "keywords": [search_keyword]}],
    }
    body = json.dumps(data)
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        result = await fetch_data(session, url, headers, body)
        date = [item["period"] for item in result["results"][0]["data"]]
        ratio_data = [item["ratio"] for item in result["results"][0]["data"]]
        df_search_trend = pd.DataFrame(
            {"date": date, search_keyword: ratio_data}
        ).set_index("date")
        return df_search_trend


async def trend_maincode(params, clients, api_url):
    standard_time = datetime.now()

    search_keywords = params.get("search_keywords", [])

    results = []
    for keyword in search_keywords:
        for client_key, client_info in clients.items():
            client_id = params["id"]
            client_secret = params["pw"]

            try:
                df_search_trend = await trend_load_async(
                    standard_time, keyword, client_id, client_secret, api_url
                )
                results.append(df_search_trend)
                break  # 성공적으로 데이터를 받아왔으므로 다음 키워드로 넘어감
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    print(f"클라이언트 오류 발생: {e.status}, 메시지='{e.message}'")
                    continue  # 다음 클라이언트 크레덴셜로 시도
                else:
                    raise  # 다른 HTTP 오류는 그대로 예외를 발생시킴

            except Exception as e:
                print(f"예상치 못한 오류 발생: {e}")
                break  # 중대한 오류로 인한 처리 중단

    return results


if __name__ == "__main__":
    # 결과 출력

    # 파라미터
    params = {
        "search_keywords": ["상속등기"],
        "id": get_secret("clients")["id_1"]["client_id"],
        "pw": get_secret("clients")["id_1"]["client_secret"],
        "api_url": "https://openapi.naver.com/v1/datalab/search",
        "name": "name",
    }

    import time
    import pandas as pd
    start = time.time()
    clients = get_secret("clients")
    api_url = "https://openapi.naver.com/v1/datalab/search"
    # 이벤트 루프 실행
    results = asyncio.run(trend_maincode(params, clients, api_url))


    for df in results:
        print(df)
    print(type(params))
    print(time.time() - start)
    print('type(params["search_keywords"]):', type(params["search_keywords"]))
    print('type(params["id"]):', type(params["id"]))
    print('type(params["pw"]):', type(params["pw"]))
    print('type(params["api_url"]):', type(params["api_url"]))
