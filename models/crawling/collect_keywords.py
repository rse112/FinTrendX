"""
이 모듈은 특정 키워드에 대한 검색 데이터를 비동기적으로 수집하기 위한 스크립트를 포함하고 있습니다.
API 클라이언트를 통해 검색 데이터를 요청하고, 수집된 데이터를 처리하여 pandas DataFrame으로 반환합니다.

주요 기능:
- API를 통한 검색 데이터의 비동기 수집
- 수집된 데이터의 전처리 및 구조화
- 검색어 별 데이터 수집 및 분석을 위한 함수 제공
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import pandas as pd
import asyncio
from api_set import APIClient
from datetime import datetime
from pytz import timezone
import time
import pandas as pd
from utils import get_secret, load_keywords



async def fetch_keyword_data(api_client, keyword, max_retries=3, retry_delay=5):
    """
    특정 키워드에 대한 검색 데이터를 비동기적으로 수집합니다.
    
    Parameters:
    - api_client (APIClient): API 클라이언트 인스턴스.
    - keyword (str): 수집할 키워드.
    - max_retries (int): 최대 재시도 횟수. 기본값은 3.
    - retry_delay (int): 재시도 사이의 대기 시간(초). 기본값은 5.
    
    Returns:
    - pd.DataFrame: 수집된 키워드 데이터를 담고 있는 DataFrame. 
      데이터 수집에 실패하면 빈 DataFrame을 반환합니다.
    """
    attempts = 0
    while attempts < max_retries:
        query = {'hintKeywords': keyword}
        try:
            response = await api_client.get_data(query)
            if 'keywordList' in response and isinstance(response['keywordList'], list):
                df = pd.DataFrame(response['keywordList'])
                df.replace('< 10', '9', inplace=True)
                columns_to_convert = ['monthlyPcQcCnt', 'monthlyMobileQcCnt']
                for column in columns_to_convert:
                    df[column] = df[column].astype('float64')
                df['monthlyTotalCnt'] = df['monthlyPcQcCnt'] + df['monthlyMobileQcCnt']
                df = df.sort_values('monthlyTotalCnt', ascending=False).reset_index(drop=True)
                df = df[['relKeyword', 'monthlyTotalCnt']]
                df.rename(columns={'relKeyword': '연관키워드', 'monthlyTotalCnt': '월간검색수_합계'}, inplace=True)
                df['검색어'] = keyword
                return df
            else:
                print(f"Unexpected response structure for keyword '{keyword}': {response}")
                attempts += 1
                await asyncio.sleep(retry_delay)
        except Exception as e:
            print(f"Error fetching data for keyword '{keyword}': {e}")
            attempts += 1
            await asyncio.sleep(retry_delay)
    print(f"Failed to fetch data for keyword '{keyword}' after {max_retries} attempts")
    return pd.DataFrame()

async def collect_keywords(srch_keyword, day):
    """
    주어진 검색어 목록에 대해 관련 키워드 데이터를 수집합니다.
    
    Parameters:
    - srch_keyword (list of str): 수집할 검색어 목록.
    - day (str): 데이터 수집 날짜(형식: "yyMMdd").
    
    Returns:
    - pd.DataFrame: 모든 검색어에 대한 관련 키워드 데이터를 담고 있는 DataFrame.
    """
    BASE_URL = get_secret("BASE_URL")
    CUSTOMER_ID = get_secret("CUSTOMER_ID")
    API_KEY = get_secret("API_KEY")
    SECRET_KEY = get_secret("SECRET_KEY")
    URI = get_secret("URI")
    METHOD = get_secret("METHOD")
    api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY, URI, METHOD)
    main_keyword = load_keywords('main_keyword.json')

    all_keywords_data = pd.DataFrame()

    for word in srch_keyword:
        if word not in main_keyword:
            continue
        for keyword in main_keyword[word]:
            df = await fetch_keyword_data(api_client, keyword)
            all_keywords_data = pd.concat([all_keywords_data, df], ignore_index=True)

    return all_keywords_data


async def main():
    """
    메인 실행 함수로, 현재 날짜에 대한 키워드 데이터 수집을 관리합니다.
    수집된 데이터를 출력하고 실행 시간을 계산합니다.
    """
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
