

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import requests
from api_set import APIClient
from utils import get_secret

def set_time_range(std_time, days_before=1, years_before=4):

    """
    기준 시간을 바탕으로 지정된 일수 전과 년수 전의 날짜를 계산하여 반환합니다.

        매개변수:
    - std_time: 기준이 되는 datetime 객체
    - days_before: 계산할 이전 일수 (기본값: 1일 전)
    - years_before: 계산할 이전 년수 (기본값: 4년 전)
    """
    end_time = (std_time - relativedelta(days=days_before)).strftime("%Y-%m-%d")
    start_time = (std_time - relativedelta(years=years_before, days=days_before)).strftime("%Y-%m-%d")
    return start_time, end_time


def trend_load(std_time, search_keyword, id, pw, url):
    """
    주어진 검색어에 대한 트렌드 데이터를 로드하여 DataFrame으로 반환합니다.
    """
    # DataFrame 초기화
    df_total = pd.DataFrame()

    # 시간 범위 설정
    start_time, end_time = set_time_range(std_time)

    # 데이터 구성
    data = {
        "startDate": start_time,
        "endDate": end_time,
        "timeUnit": "date",
        "keywordGroups": [
            {
                "groupName": search_keyword,
                "keywords": [search_keyword]
            }
        ]
    }

    # Python 사전을 JSON 문자열로 변환
    body = json.dumps(data)

    # 요청 헤더 설정
    headers = {
        "X-Naver-Client-Id": id,
        "X-Naver-Client-Secret": pw,
        "Content-Type": "application/json"
    }

    try:
        # POST 요청으로 데이터 로드
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()

        # JSON 데이터 로드 및 DataFrame 생성
        result = response.json()
        date = [item['period'] for item in result['results'][0]['data']]
        ratio_data = [item['ratio'] for item in result['results'][0]['data']]

        df_search_trend = pd.DataFrame({'date': date, f'{search_keyword}': ratio_data})
        df_total = df_search_trend.set_index('date')

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 오류 발생: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"연결 오류 발생: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"시간 초과 오류 발생: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"요청 오류 발생: {req_err}")
    except Exception as err:
        print(f"예상치 못한 오류 발생: {err}")

    return df_total



if __name__ == "__main__":
    import time
    BASE_URL = get_secret("BASE_URL")
    CUSTOMER_ID = get_secret("CUSTOMER_ID")
    API_KEY = get_secret("API_KEY")
    SECRET_KEY = get_secret("SECRET_KEY")
    URI = get_secret("URI")
    METHOD = get_secret("METHOD")
    # API 클라이언트 인스턴스 생성
    api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY,URI,METHOD)
    # 검색 기준일
    standard_time = datetime.now()

    #api 아이디비번 가져오기
    client_id = get_secret("clients")["id_1"]["client_id"]
    client_secret = get_secret("clients")["id_1"]["client_secret"]

    # 검색어 설정
    search_keywords = ["디도스", "클라우드 보안", "사이버 공격","주식","비트코인","테슬라","삼성전자","네이버","카카오"]

    # API 요청 URL
    api_url = "https://openapi.naver.com/v1/datalab/search"
    start=time.time()
    # 데이터 로드
    for word in search_keywords:
        
        trend_data = trend_load(standard_time, word, client_id, client_secret, api_url)
        print(trend_data)
    # 로드한 데이터 확인
    print(time.time()-start)
    
