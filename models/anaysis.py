from concurrent.futures import ProcessPoolExecutor, as_completed
from models.crawling.select_keyword import (
    select_keyword,
    rising_keyword_analysis,
    monthly_rule,
)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),  '..'))
import utils.utils as utils

formatted_today, today_date = utils.get_today_date()


def execute_analysis(results, month_rule_list, rising_list, select_list):
    with ProcessPoolExecutor() as executor:
        future_to_function = (
            {
                executor.submit(monthly_rule, keyword_data, today_date, "month"): (
                    "monthly",
                    keyword_data,
                )
                for keyword_group in results
                for keyword_data in keyword_group
            }
            | {
                executor.submit(
                    rising_keyword_analysis, keyword_df, today_date, period
                ): ("rising", keyword_df, period)
                for keyword_df_group in results
                for keyword_df in keyword_df_group
                for period in ["weekly", "month"]
            }
            | {
                executor.submit(select_keyword, keyword_df, today_date, period): (
                    "select",
                    keyword_df,
                    period,
                )
                for keyword_df_group in results
                for keyword_df in keyword_df_group
                for period in ["daily", "weekly", "month"]
            }
        )

        for future in as_completed(future_to_function):
            function_type, *args = future_to_function[future]
            try:
                data = future.result()
                # 여기에 결과 처리 로직을 삽입
                if function_type == "monthly":
                    month_rule_list.append(data)  # 월별 분석 결과 처리
                elif function_type == "rising":
                    if args[-1] == "weekly":
                        rising_list[0].append(data)  # 주별 상승 결과
                    elif args[-1] == "month":
                        rising_list[1].append(data)  # 월별 상승 결과
                elif function_type == "select":
                    if args[-1] == "daily":
                        select_list[0].append(data)  # 일별 선택 결과
                    elif args[-1] == "weekly":
                        select_list[1].append(data)  # 주별 선택 결과
                    elif args[-1] == "month":
                        select_list[2].append(data)  # 월별 선택 결과
            except Exception as exc:
                print(f"{function_type} function generated an exception: {exc}")


# 형식에 맞게 결과를 처리하는 함수
def process_results(results, info_key="InfoData", additional_data=None):
    processed_results = []
    for result in results:
        if not all(value is None for value in result):
            result[1][info_key] = result[2]
            if additional_data:
                for key, value in additional_data.items():
                    result[1][key] = value
            processed_results.append(result[1])
    return processed_results


def process_results_month(results, info_key="InfoData", additional_data=None):
    processed_results = []
    for result in results:
        if not all(value is None for value in result):
            result[1][info_key] = result[2]
            result[1]["RisingMonth"] = 0

            # result[3]이 리스트의 리스트인지, 단일 리스트인지 판별하여 적절히 처리
            if result[3] and isinstance(result[3][0], list):
                # result[3]이 리스트의 리스트라면, 각 내부 리스트를 정렬
                sorted_lists = [sorted(months) for months in result[3]]
            else:
                # result[3]이 단일 리스트라면, 바로 정렬
                sorted_lists = sorted(result[3])
            for i, month in enumerate(
                sorted_lists
            ):  # 이제 sorted_lists는 정렬된 단일 리스트를 가리킴
                if i < len(result[1]):
                    result[1].loc[i, "RisingMonth"] = month
                else:
                    break
            processed_results.append(result[1])
    return processed_results
