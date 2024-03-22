import sys
import os

# 현재 스크립트의 경로를 기준으로 상위 디렉토리의 절대 경로를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import utils
from pytz import timezone
import time
import urllib.request
import urllib
from dateutil.relativedelta import relativedelta
import json
from tqdm import tqdm


# 검색어별 관련 블로그 수집 함수
def blog(client_id, client_secret, query, display, start, sort):
    encText = urllib.parse.quote(query)
    url = (
        "https://openapi.naver.com/v1/search/blog?query="
        + encText
        + "&display="
        + str(display)
        + "&start="
        + str(start)
        + "&sort="
        + sort
    )

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        response_json = json.loads(response_body)
    else:
        print("Error Code:" + rescode)

    return pd.DataFrame(response_json["items"])


def load_list_from_text(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]


# 최근 1년간 검색어와 관련된 블로그 수집
def blog_result(types, std_time):
    client_id = utils.get_secret("Naver_blog_id")
    client_secret = utils.get_secret("Naver_blog_pw")
    # 최근일자(=기준일자 하루전)
    end_time = std_time - relativedelta(days=1)
    # 시작일자(=2년전)
    start_time = std_time - relativedelta(weeks=1) - relativedelta(days=1)
    end_time = end_time.strftime("%Y-%m-%d")
    start_time = start_time.strftime("%Y-%m-%d")

    display = 100
    start = 1
    sort = "date"

    blog_active = []

    leng = len(types)
    print()
    for i in range(0, leng):
        query = f"{types[i]}"

        result_all = pd.DataFrame()
        for i in range(0, 10):
            start = 1 + 100 * i
            time.sleep(0.1)
            result = blog(client_id, client_secret, query, display, start, sort)

            result_all = pd.concat([result_all, result])
        result_all.reset_index(inplace=True, drop=True)

        result_all["postdate"] = pd.to_datetime(result_all["postdate"])

        length = len(
            result_all[
                (result_all["postdate"] >= start_time)
                & ((result_all["postdate"] <= end_time))
            ].index
        )

        # 활동성 (1000개 중 최근 일주일동안 블로그 발간 비율)
        result = round(length / 1000 * 100, 3)
        blog_active.append(result)

    return blog_active


# 현재 시간 설정
today = datetime.now(timezone("Asia/Seoul"))
formatted_today = today.strftime("%y%m%d")


def activity_rate(keywords_path):
    keywords = load_list_from_text(keywords_path)
    # 각 검색어에 대한 활동성 지수를 저장할 리스트
    activity_rates = []

    # 각 검색어에 대해 blog_result 함수를 호출, tqdm으로 래핑하여 진행 상태 표시
    for keyword in tqdm(keywords, desc="Processing Keywords"):

        activity_rate = blog_result(
            [keyword], today
        )  # blog_result 함수는 리스트를 입력으로 받으므로, keyword를 리스트로 전달
        activity_rates.append(
            activity_rate[0]
        )  # 반환값이 리스트 형태이므로, 첫 번째 요소만 추가

    # 결과 데이터프레임 생성
    df_results = pd.DataFrame({"Keyword": keywords, "Activity Rate": activity_rates})
    # 결과 출력

    # CSV 파일로 저장
    df_results.to_csv(
        f"./data/target_keywords/{formatted_today}/keyword_activity_rates.csv",
        index=False,
    )
    print("Saved to activity_rates.csv")


if __name__ == "__main__":

    target_keywords = load_list_from_text(
        "./data/target_keywords/240313/target_keywords.txt"
    )
    target_keywords = ["비상금대출", "가상자산"]
    keywords = ["가상자산", "비상금대출"]
    client_id = utils.get_secret("Naver_blog_id")
    client_secret = utils.get_secret("Naver_blog_pw")
    # types = ["신용카드발급", "파이썬"]  # 검색하고자 하는 키워드 목록
    std_time = datetime.now()  # 기준 시간 설정
    # target_keywords=['파이썬','망고']
    # 비동기 메인 함수 실행
    activity_rate(target_keywords)
