# import os
# import sys
# import time
# import random
# import pandas as pd
# import numpy as np
# from itertools import combinations, permutations
# from dtw import *
# import json
# import matplotlib.pyplot as plt
# from statsmodels.tsa.seasonal import seasonal_decompose
# import statsmodels.api as sm
# import pickle
# from pytz import timezone
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
# from collections import defaultdict
# from pytrends.request import TrendReq
# import nest_asyncio
# import asyncio

# import utils
# import models.crawling.trend as trend
# from models.naver.blog import blog_result_async
# from api_set import APIClient
# from models.crawling.collect_keywords import main
# from datetime import datetime
# from models.crawling.select_keyword import (
#     select_keyword,
#     rising_keyword_analysis,
#     monthly_rule,
# )
# import nest_asyncio

# nest_asyncio.apply()
# BASE_URL = utils.get_secret("BASE_URL")
# CUSTOMER_ID = utils.get_secret("CUSTOMER_ID")
# API_KEY = utils.get_secret("API_KEY")
# SECRET_KEY = utils.get_secret("SECRET_KEY")
# URI = utils.get_secret("URI")
# METHOD = utils.get_secret("METHOD")
# # API 클라이언트 인스턴스 생성
# api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY, URI, METHOD)


# # 키 로드
# keywords_data = utils.load_keywords("main_keyword.json")

# # 오늘의 날짜 가져오기
# formatted_today, day = utils.get_today_date()

# utils.make_directory("./data")
# utils.make_directory("./data/rl_srch")
# utils.make_directory(f"./data/rl_srch/{day}")  # 키워드별 연관검색어 리스트 저장

# # 검색어 리스트와 결과 저장 경로 설정
# srch_keyword = ["keyword_final"]
# save_path = "./data/rl_srch/"

# # 연관검색어 트렌드 데이터 수집
# collected_keywords_data = asyncio.run(main(srch_keyword, day))


# # '검색어'별로 그룹화된 DataFrame을 리스트에 저장
# df_list = [group for _, group in collected_keywords_data.groupby("검색어")]

# collected_keywords_data = utils.merge_and_mark_duplicates_limited(df_list)


# collected_keywords_data = utils.add_client_info(collected_keywords_data)
# new_columns = [
#     "일별급상승",
#     "주별급상승",
#     "월별급상승",
#     "주별지속상승",
#     "월별지속상승",
#     "월별규칙성",
# ]

# for column in new_columns:
#     collected_keywords_data[column] = 0


# def groupped_df(name, collected_keywords_data):
#     grouped = collected_keywords_data.groupby(name)
#     df_list = [group for _, group in grouped]
#     return df_list


# df_list = groupped_df("id", collected_keywords_data)


# # 비동기 메인 함수 수정
# async def trend_main(df, clients):
#     # 파라미터 설정
#     params = {
#         "search_keywords": list(df["연관키워드"]),
#         "id": df["id"].iloc[0],
#         "pw": df["pw"].iloc[0],
#         "api_url": "https://openapi.naver.com/v1/datalab/search",
#         "name": "연관검색어",
#     }
#     api_url = "https://openapi.naver.com/v1/datalab/search"

#     # trend_maincode 함수 실행
#     results = await trend.trend_maincode(params, clients, api_url)
#     return results


# async def run_all(df_list, clients):
#     tasks = [trend_main(df, clients) for df in df_list]
#     results = await asyncio.gather(*tasks)
#     return results


# clients = utils.get_secret("clients")  # clients 정보를 로드
# # 이벤트 루프 실행

# trend_main_data = asyncio.run(run_all(df_list, clients))
# # results = trend_main_data.copy()

# # select_periods = ["daily", "weekly", "month"]
# # rising_periods = ["weekly", "month"]

# # formatted_today, today_date = utils.get_today_date()
# # month_rule_list = []
# # select_list = [[], [], []]

# # rising_list = [[], []]
# # rising_month_list = []
# # # 월별, 주별, 일별 키워드 분석 실행

# # # 각 분석 기간에 대해 결과 집합을 순회합니다.
# # for keyword_group in results:
# #     # 키워드 그룹의 각 키워드 데이터프레임에 대해 순회합니다.
# #     for keyword_data in keyword_group:
# #         # 월별 규칙을 적용하여 결과를 가져옵니다.
# #         monthly_data, monthly_chart, similarity_rate, rising_months = monthly_rule(
# #             keyword_data, today_date, "month"
# #         )

# #         if monthly_data is not None:
# #             # 결과 데이터프레임의 열 이름을 가져옵니다.
# #             column_names = monthly_data.columns
# #             rising_month_list.append([rising_months, column_names[0]])
# #             # 결과 데이터프레임에서 값 리스트를 추출합니다.
# #             data_values_list = monthly_data[column_names].values
# #             # 월별 차트에 데이터 값을 추가합니다.
# #             monthly_chart["Indicator"] = data_values_list
# #             monthly_chart["InfoData"] = similarity_rate
# #             # 상승 월 정보를 추가합니다. 상승 월이 없는 경우 0으로 설정합니다.
# #             monthly_chart["RisingMonth"] = 0

# #             # 최종 결과 리스트에 수정된 월별 차트를 추가합니다.
# #             month_rule_list.append(monthly_chart)

# # # 주별, 월별 상승 키워드 분석 실행
# # rising_analysis_periods = ["weekly", "month"]
# # i = 0
# # for period in rising_analysis_periods:
# #     for keyword_df_group in results:
# #         for keyword_df in keyword_df_group:
# #             rising_tmp, rising_graph, rising_info = rising_keyword_analysis(
# #                 keyword_df, today_date, period
# #             )
# #             if rising_tmp is not None:
# #                 column_names = rising_tmp.columns
# #                 data_values_list = rising_tmp[column_names].values
# #                 rising_graph["Indicator"] = data_values_list
# #                 rising_graph["InfoData"] = rising_info

# #                 rising_list[i].append(rising_graph)
# #     i = i + 1


# # i = 0
# # # 일별, 주별, 월별 키워드 선택 실행
# # for period in select_periods:
# #     for keyword_df_group in results:
# #         for keyword_df in keyword_df_group:
# #             selected_tmp, selected_graph, selected_info = select_keyword(
# #                 keyword_df, today_date, period
# #             )
# #             if selected_graph is not None:
# #                 # 데이터프레임의 열 이름을 출력합니다.
# #                 selected_graph["InfoData"] = selected_info
# #                 select_list[i].append(selected_graph)
# #             else:
# #                 pass
# #     i += 1


# # # 리스트와 유형을 매핑
# # lists_and_types = [
# #     (select_list[0], "일별급상승"),
# #     (select_list[1], "주별급상승"),
# #     (select_list[2], "월별급상승"),
# #     (rising_list[0], "주별지속상승"),
# #     (rising_list[1], "월별지속상승"),
# #     (month_rule_list, "월별규칙성"),
# # ]


# # # 각 리스트에 대한 유형 라벨 추가 및 병합
# # def process_and_concat(df_list, label):
# #     for df in df_list:
# #         df["유형"] = label
# #     return pd.concat(df_list).reset_index(drop=True)


# # # 모든 리스트를 처리하고 하나의 데이터프레임으로 병합
# # processed_dfs = [
# #     process_and_concat(df_list, label) for df_list, label in lists_and_types
# # ]

# # graph_result = pd.concat(processed_dfs).reset_index(drop=True)

# # # 불필요한 컬럼 삭제 및 '주간지속상승'을 '주별지속상승'으로 수정
# # graph_result = graph_result.drop(columns=["InfoData", "Indicator", "RisingMonth"])
# # graph_result["유형"].replace({"주간지속상승": "주별지속상승"}, inplace=True)

# # # 정렬
# # graph_result.sort_values(
# #     by=["연관검색어", "유형", "검색일자"], ascending=[True, True, True], inplace=True
# # )
# # # 최종 결과 출력
# # graph_result.reset_index(drop=True, inplace=True)


# # print(1)
