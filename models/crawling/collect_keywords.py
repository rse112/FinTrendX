import sys
import os
# 현재 스크립트의 경로를 기준으로 상위 디렉토리의 절대 경로를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import pandas as pd
import asyncio
from api_set import APIClient
from datetime import datetime
from pytz import timezone
import time
import pandas as pd
import asyncio
from utils import get_secret, load_keywords
from api_set import APIClient
import asyncio
from api_set import APIClient

async def collect_keywords(srch_keyword, day):
    BASE_URL = get_secret("BASE_URL")
    CUSTOMER_ID = get_secret("CUSTOMER_ID")
    API_KEY = get_secret("API_KEY")
    SECRET_KEY = get_secret("SECRET_KEY")
    URI = get_secret("URI")
    METHOD = get_secret("METHOD")
    api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY, URI, METHOD)
    main_keyword = load_keywords('main_keyword.json')

    all_keywords_data = pd.DataFrame()
    retry_delay = 5  # 재시도 전 대기 시간 (초)
    max_retries = 3  # 최대 재시도 횟수

    for word in srch_keyword:
        if word in main_keyword:
            for keyword in main_keyword[word]:
                attempts = 0
                while attempts < max_retries:
                    query = {
                        'hintKeywords': keyword
                    }
                    try:
                        response = await api_client.get_data(query)
                        if 'keywordList' in response and isinstance(response['keywordList'], list):
                            df = pd.DataFrame(response['keywordList'])
                            df.replace('< 10', '9', inplace=True)
                            columns_to_convert = ['monthlyPcQcCnt', 'monthlyMobileQcCnt']
                            for column in columns_to_convert:
                                df[column] = df[column].astype('float64')
                            df['monthlyTotalCnt'] = df['monthlyPcQcCnt'] + df['monthlyMobileQcCnt']
                            df = df[['relKeyword', 'monthlyTotalCnt']]
                            df.rename(columns={'relKeyword': '연관키워드', 'monthlyTotalCnt': '월간검색수_합계'}, inplace=True)
                            df['검색어'] = keyword
                            all_keywords_data = pd.concat([all_keywords_data, df], ignore_index=True)
                            break  # 성공적으로 데이터를 받았으니 반복문 종료
                        else:
                            print(f"Unexpected response structure for keyword '{keyword}': {response}")
                            attempts += 1
                            await asyncio.sleep(retry_delay)  # 재시도 전 대기
                    except Exception as e:
                        print(f"Error fetching data for keyword '{keyword}': {e}")
                        attempts += 1
                        await asyncio.sleep(retry_delay)  # 재시도 전 대기
                if attempts == max_retries:
                    print(f"Failed to fetch data for keyword '{keyword}' after {max_retries} attempts")

    return all_keywords_data


async def main():
    today = datetime.now(timezone('Asia/Seoul'))
    day = today.strftime("%y%m%d")
    srch_keyword = ["keyword_final"]
    collected_data = await collect_keywords(srch_keyword, day)
    print(collected_data)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"Execution time: {end - start} seconds")
