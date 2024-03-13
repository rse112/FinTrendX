import os
import sys
import time
import random
import requests
import pandas as pd
import numpy as np
import hashlib, hmac, base64
from itertools import combinations, permutations
from dtw import *
import json
import urllib.request
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm
import pickle
from pytz import timezone
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from pytrends.request import TrendReq
import nest_asyncio
import asyncio
from models.naver.blog import blog_result_async

from api_set import APIClient
from models.crawling.select_keyword import (
    select_keyword,
    rising_keyword_analysis,
    monthly_rule,
)
import utils
import models.crawling.trend as trend

# API 설정
from utils import get_secret

BASE_URL = get_secret("BASE_URL")
CUSTOMER_ID = get_secret("CUSTOMER_ID")
API_KEY = get_secret("API_KEY")
SECRET_KEY = get_secret("SECRET_KEY")
URI = get_secret("URI")
METHOD = get_secret("METHOD")
# API 클라이언트 인스턴스 생성
api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY, URI, METHOD)


# 키 로드
from utils import load_keywords

keywords_data = load_keywords("main_keyword.json")

from utils import get_today_date

# 오늘의 날짜 가져오기
formatted_today, day = get_today_date()


# 결과 저장 폴더 생성
from utils import make_directory

make_directory("./data")
make_directory("./data/rl_srch")
make_directory(f"./data/rl_srch/{day}")  # 키워드별 연관검색어 리스트 저장


# 검색어 리스트와 결과 저장 경로 설정
srch_keyword = ["keyword_final"]
save_path = "./data/rl_srch/"
print(api_client.base_url)

import os
import csv
import datetime
import asyncio
import pandas as pd

# 필요한 경우 비동기를 위한 nest_asyncio 적용
import nest_asyncio

nest_asyncio.apply()

from models.crawling.collect_keywords import collect_keywords


async def main(srch_keyword, day):
    # 오늘 날짜로 폴더 경로 생성
    folder_path = "./data/rl_srch/" + datetime.datetime.now().strftime("%y%m%d")
    file_path = f"{folder_path}/collected_keywords.csv"

    # 폴더가 존재하는지 확인
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 파일이 존재하는지 확인
    if os.path.isfile(file_path):
        # 파일이 존재하면, 데이터를 읽어옵니다.
        collected_keywords_data = pd.read_csv(file_path)
    else:
        # 파일이 없으면, collect_keywords 함수를 호출해서 데이터를 수집합니다.
        collected_keywords_data = await collect_keywords(srch_keyword, day)
        # 결과를 CSV로 저장
        collected_keywords_data.to_csv(file_path, index=False)

    return collected_keywords_data


collected_keywords_data = asyncio.run(main(srch_keyword, day))
from utils import merge_and_mark_duplicates_limited

# '검색어'별로 그룹화된 DataFrame을 리스트에 저장
df_list = [group for _, group in collected_keywords_data.groupby("검색어")]

collected_keywords_data = merge_and_mark_duplicates_limited(df_list)


def add_client_info(collected_keywords_data, start_id_index=1):
    clients = utils.get_secret("clients")
    start_id_index = 1
    clients = utils.get_secret("clients")
    # ID와 PW 컬럼을 데이터프레임에 추가하는 로직
    total_rows = len(collected_keywords_data)
    ids = []
    pws = []

    for i in range(total_rows):
        # 현재 id 인덱스 계산 (start_id_index를 기준으로)
        current_id_index = ((i // 500) + start_id_index) % len(clients)
        current_id_key = f"id_{current_id_index}"

        # 현재 id와 pw 할당
        current_id = clients[current_id_key]["client_id"]
        current_pw = clients[current_id_key]["client_secret"]

        ids.append(current_id)
        pws.append(current_pw)

    # ID와 PW 컬럼 추가
    collected_keywords_data["id"] = ids
    collected_keywords_data["pw"] = pws

    return collected_keywords_data


collected_keywords_data = add_client_info(collected_keywords_data)
new_columns = [
    "일별급상승",
    "주별급상승",
    "월별급상승",
    "주별지속상승",
    "월별지속상승",
    "월별규칙성",
]

for column in new_columns:
    collected_keywords_data[column] = 0


def groupped_df(name, collected_keywords_data):
    grouped = collected_keywords_data.groupby(name)
    df_list = [group for _, group in grouped]
    return df_list


df_list = groupped_df("id", collected_keywords_data)


# 비동기 메인 함수 수정
async def trend_main(df, clients):
    # 파라미터 설정
    params = {
        "search_keywords": list(df["연관키워드"]),
        "id": df["id"].iloc[0],
        "pw": df["pw"].iloc[0],
        "api_url": "https://openapi.naver.com/v1/datalab/search",
        "name": "연관검색어",
    }
    api_url = "https://openapi.naver.com/v1/datalab/search"

    # trend_maincode 함수 실행
    results = await trend.trend_maincode(params, clients, api_url)
    return results


async def run_all(df_list, clients):
    tasks = [trend_main(df, clients) for df in df_list]
    results = await asyncio.gather(*tasks)
    return results


clients = get_secret("clients")  # clients 정보를 로드
# 이벤트 루프 실행

trend_main_data = asyncio.run(run_all(df_list, clients))
results = trend_main_data.copy()

start_time = time.time()
select_periods = ["daily", "weekly", "month"]
rising_periods = ["weekly", "month"]

formatted_today, today_date = utils.get_today_date()
month_rule_list = []
select_list = [[], [], []]

rising_list = [[], []]
rising_month_list = []
# 월별, 주별, 일별 키워드 분석 실행

# 각 분석 기간에 대해 결과 집합을 순회합니다.
for keyword_group in results:
    # 키워드 그룹의 각 키워드 데이터프레임에 대해 순회합니다.
    for keyword_data in keyword_group:
        # 월별 규칙을 적용하여 결과를 가져옵니다.
        monthly_data, monthly_chart, similarity_rate, rising_months = monthly_rule(
            keyword_data, today_date, "month"
        )

        if monthly_data is not None:
            # 결과 데이터프레임의 열 이름을 가져옵니다.
            column_names = monthly_data.columns
            rising_month_list.append([rising_months, column_names[0]])
            # 결과 데이터프레임에서 값 리스트를 추출합니다.
            data_values_list = monthly_data[column_names].values
            # 월별 차트에 데이터 값을 추가합니다.
            monthly_chart["Indicator"] = data_values_list
            monthly_chart["InfoData"] = similarity_rate
            # 상승 월 정보를 추가합니다. 상승 월이 없는 경우 0으로 설정합니다.
            monthly_chart["RisingMonth"] = 0

            # 최종 결과 리스트에 수정된 월별 차트를 추가합니다.
            month_rule_list.append(monthly_chart)

# 주별, 월별 상승 키워드 분석 실행
rising_analysis_periods = ["weekly", "month"]
i = 0
for period in rising_analysis_periods:
    for keyword_df_group in results:
        for keyword_df in keyword_df_group:
            rising_tmp, rising_graph, rising_info = rising_keyword_analysis(
                keyword_df, today_date, period
            )
            if rising_tmp is not None:
                column_names = rising_tmp.columns
                data_values_list = rising_tmp[column_names].values
                rising_graph["Indicator"] = data_values_list
                rising_graph["InfoData"] = rising_info

                rising_list[i].append(rising_graph)
    i = i + 1


i = 0
# 일별, 주별, 월별 키워드 선택 실행
for period in select_periods:
    for keyword_df_group in results:
        for keyword_df in keyword_df_group:
            selected_tmp, selected_graph, selected_info = select_keyword(
                keyword_df, today_date, period
            )
            if selected_graph is not None:
                # 데이터프레임의 열 이름을 출력합니다.
                selected_graph["InfoData"] = selected_info
                select_list[i].append(selected_graph)
            else:
                pass
    i += 1

import pandas as pd

# 리스트와 유형을 매핑
lists_and_types = [
    (select_list[0], "일별급상승"),
    (select_list[1], "주별급상승"),
    (select_list[2], "월별급상승"),
    (rising_list[0], "주별지속상승"),
    (rising_list[1], "월별지속상승"),
    (month_rule_list, "월별규칙성"),
]


# 각 리스트에 대한 유형 라벨 추가 및 병합
def process_and_concat(df_list, label):
    for df in df_list:
        df["유형"] = label
    return pd.concat(df_list).reset_index(drop=True)


# 모든 리스트를 처리하고 하나의 데이터프레임으로 병합
processed_dfs = [
    process_and_concat(df_list, label) for df_list, label in lists_and_types
]

graph_result = pd.concat(processed_dfs).reset_index(drop=True)

# 불필요한 컬럼 삭제 및 '주간지속상승'을 '주별지속상승'으로 수정
graph_result = graph_result.drop(columns=["InfoData", "Indicator", "RisingMonth"])
graph_result["유형"].replace({"주간지속상승": "주별지속상승"}, inplace=True)

# 정렬
graph_result.sort_values(
    by=["연관검색어", "유형", "검색일자"], ascending=[True, True, True], inplace=True
)

# 최종 결과 출력
graph_result.reset_index(drop=True, inplace=True)
