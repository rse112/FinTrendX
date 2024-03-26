import sys
import os

# 현재 스크립트의 경로를 기준으로 상위 디렉토리의 절대 경로를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from dtw import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import utils
from api_set import APIClient
import statsmodels.api as sm
import asyncio
from models.crawling.trend import trend_maincode
import time
from datetime import datetime
import pytz

formatted_today, day = utils.get_today_date()


def create_result_graph(result_tmp, result_tmp_gph, today, mode):
    """
    검색 결과와 관련 데이터를 바탕으로 결과 데이터 프레임을 생성하는 함수.

    Parameters:
    - result_tmp: 원본 검색 결과 데이터 프레임.
    - result_tmp_gph: 그래프용 검색 결과 데이터 프레임.
    - formatted_today: 기준일자 문자열.
    - mode: 검색 유형 문자열.

    Returns:
    - result_graph: 생성된 결과 데이터 프레임.
    """
    if mode == "daily":
        mode_str = "일별"
    elif mode == "weekly":
        mode_str = "주별"
    else:
        mode_str = "월별"
    result_graph = pd.DataFrame()
    result_graph["검색일자"] = result_tmp_gph.index
    result_graph["기준일자"] = formatted_today
    result_graph["유형"] = f"{mode_str}급상승"
    result_graph["연관검색어"] = result_tmp_gph.columns[0]
    result_graph["검색량"] = result_tmp_gph.values
    result_graph = result_graph[
        ["기준일자", "유형", "연관검색어", "검색일자", "검색량"]
    ]
    return result_graph


# 급상승 키워드 조건을 평가하고, 해당하는 경우 데이터와 상승률을 반환함.
def check_surge_conditions(
    last, last_2, var, result_tmp, result_tmp_gph, table_graph, mode
):
    """
    급상승 조건을 확인하고 결과를 반환하는 함수.
    round((last - last_2)/last_2 * 100,2) : 지표(추세성, 상승률)
    """
    # print(result_tmp)
    # print(result_tmp_gph)
    vars = 200
    if mode == "daily":
        period_str = "일별"
        last_Boundary = 85
    elif mode == "weekly":
        period_str = "주별"
        last_Boundary = 90
        vars = 350
    else:
        period_str = "월별"
        last_Boundary = 85

    rate = round((last - last_2) / last_2 * 100, 2)

    # 그림용 테이블 생성
    result_graph = create_result_graph(
        result_tmp, result_tmp_gph, formatted_today, mode
    )
    recent = sloop(result_tmp.iloc[-3:,])



    if mode == "daily" or mode == "weekly":
        if var > vars:


            return None, None, None

        if (last > last_2 * 2.0) & (last >= 60):
            print(f"{period_str} 급상승 키워드 발견: {table_graph.columns[0]}")
            print(33)
            return result_graph, result_graph, rate

        elif (last >= 95) & (last > last_2):
            print(22)
            print(f"{period_str} 급상승 키워드 발견: {table_graph.columns[0]}")

            

            return result_graph, result_graph, rate
        elif (
            (last_2 * 2.0 > 100)
            & (last >= last_Boundary)
            & (last > last_2)
            & ((last - last_2) > 5)
        ):
            print(f"{period_str} 급상승 키워드 발견: {table_graph.columns[0]}")

            print(11)
            return result_graph, result_graph, rate
        else:
            return None, None, None
        
    else:
        if last == 100:
            print(f"{period_str} 급상승 키워드 발견 : {table_graph.columns[0]}")

            return result_graph, result_graph, rate
        else :
            if (last >= last_2 * 2.0) & (last >= 60) & (recent >= 15) :

                print(f'월별 급상승 키워드 발견 : {result_tmp.columns[0]}')

                return result_tmp, result_graph, rate

            elif (last >= 95) & (last > last_2)  & (recent >= 15) :

                print(f'월별 급상승 키워드 발견 : {result_tmp.columns[0]}')

                return result_tmp, result_graph, rate

            elif (last_2 * 2.0 > 100) & (last >= 85) & (last > last_2) & ((last - last_2) > 5)  & (recent >= 15) :

                print(f'월별 급상승 키워드 발견 : {result_tmp.columns[0]}')

                return result_tmp, result_graph, rate

            else :
                return None, None, None






# 주어진 날짜와 기간을 바탕으로 데이터 분석 기간을 설정하고, 해당 기간의 데이터를 필터링하여 반환함.
def set_analysis_period(table, today, days=0, year=0, yearss=0,mode="weekly"):
    try:
        #        year = 2
        # years = 3
        std_time = datetime.strptime(today, "%y%m%d")
        day = relativedelta(days=days)
        years_delta = relativedelta(years=yearss) #3
        year_delta = relativedelta(years=year) #2
        # 날짜 계산
        end_time = std_time - day
        start_time = std_time - year_delta - day # start_time = 지금-2년
        start_before = std_time - years_delta - day
        end_time_str = end_time.strftime("%Y-%m-%d")
        start_time_str = start_time.strftime("%Y-%m-%d")
        start_before_str = start_before.strftime("%Y-%m-%d")

        # 분석 기간 설정
        table.index = pd.to_datetime(table.index)

        table_tmp = table[
            (table.index >= start_time_str) & (table.index <= end_time_str)
        ]
        table_graph = table[
            (table.index >= start_before_str) & (table.index <= end_time_str)
        ]
        if mode == "daily":
            dateLimit = 350
            # print(result_tmp)

        elif mode == "weekly":
            dateLimit = 700
        else:
            dateLimit = 1080
        if len(table_tmp) < dateLimit:
            return None, None, None
        return end_time_str, table_tmp, table_graph

    except Exception as e:

        print(f"An error occurred in set_analysis_period: {e}")

        return None, None, None


# 데이터프레임의 첫 번째 열에 대해 선형 회귀를 수행하고 기울기를 반환함.
def sloop(dataframe):
    """ """
    df = dataframe.copy()
    df["time"] = range(1, len(df) + 1)
    y = df.iloc[:, 0]
    X = df["time"]
    X = sm.add_constant(X)

    ols_fit = sm.OLS(y, X).fit()
    b1 = ols_fit.params.time

    return b1


# 데이터 전처리 및 분석 기간 설정을 위한 함수.
def preprocess_data(end_time, table_tmp, table_graph, mode, period, Gap):
    """
    데이터 전처리 및 분석 기간 설정을 위한 함수.

    Parameters:
    - table_tmp: DataFrame, 분석 대상이 되는 테이블
    - table_graph: DataFrame, 그래프 작성을 위한 테이블
    - mode: str, 분석 모드 ('daily', 'weekly', 'month')
    - period: int, 데이터 집계 주기
    - Gap: int, 데이터 집계 간격

    Returns:
    - result_tmp: DataFrame, 처리된 결과 데이터
    - result_tmp_gph: DataFrame, 그래프 작성용 처리된 결과 데이터
    - error: str, 에러 메시지 (데이터 포인트 부족시)
    """

    if mode == "daily":
        # 일별 데이터는 이미 최적화된 상태이므로 추가 처리 없이 반환
        result_tmp = table_tmp / table_tmp.max() * 100
        result_tmp_gph = table_graph / table_graph.max() * 100
        return result_tmp, result_tmp_gph
    
    else:
        # 주별 또는 월별 데이터 집계
        tmp_list = []
        for i in range(0, period[0], 1):
            if i == 0:
                days_data = table_tmp.iloc[-(Gap * (i + 1)) :]
            else:
                days_data = table_tmp.iloc[-(Gap * (i + 1)) : -(Gap * i)]
            tmp_list.append(days_data.sum())

        tmp_frame = pd.DataFrame(tmp_list).iloc[::-1].reset_index(drop=True)
        # 그래프 작성용 데이터 집계
        tmp_list_graph = []

        for j in range(
            0, period[1], 1
        ):  
            if j == 0:

                days_data_graph = table_graph.iloc[-(Gap * (j + 1)) :]

            else:
                days_data_graph = table_graph.iloc[-(Gap * (j + 1)) : -(Gap * j)]

                
            tmp_list_graph.append(days_data_graph.sum())
        tmp_graph = pd.DataFrame(tmp_list_graph).iloc[::-1].reset_index(drop=True)

        # 상대적 검색량 조정
        result_tmp = tmp_frame / tmp_frame.max() * 100
        result_tmp_gph = tmp_graph / tmp_graph.max() * 100
        if mode == "weekly":
            freq = "7d"
        elif mode == "month":
            freq = "28d"
        result_tmp.index = pd.date_range(
            end=f"{end_time}", periods=len(result_tmp.index), freq=freq
        )
        result_tmp_gph.index = pd.date_range(
            end=f"{end_time}", periods=len(result_tmp_gph.index), freq=freq
        )

        return result_tmp, result_tmp_gph


# 주어진 모드에 따라 데이터를 준비하고 전처리하는 함수.
def prepare_data(table, today, mode, days=None, year=None, years=None):
    """
    주어진 모드에 따라 데이터를 준비하고 전처리하는 함수.

    Parameters:
    - table: DataFrame, 분석 대상 데이터
    - today: datetime, 현재 날짜
    - mode: str, 분석 모드 ('daily', 'weekly', 'month')

    Returns:
    - result_tmp: DataFrame, 처리된 데이터
    - result_tmp_gph: DataFrame, 그래프용 처리된 데이터
    - error: str, 에러 메시지 (있을 경우)
    """
    if mode == "daily":

        days = 1
        year = 1
        years = 3

        period = [1, 1]
        Gap = 1

    elif mode == "weekly":

        period = [104, 156]
        Gap = 7
        days = 1
        year = 2
        years = 3

    elif mode == "month":

        period = [36, 36]
        Gap = 28
        days = 1
        year = 3
        years = 3

    else:
        pass

    ##############################################
    end_time, table_tmp, table_graph = set_analysis_period(
        table, today, days=days, year=year, yearss=years,mode=mode
    )





    if end_time is None or table_tmp is None or table_graph is None:

        return None, None, None

    else:

        result_tmp, result_tmp_gph = preprocess_data(
            end_time,
            table_tmp,
            table_graph,
            mode=mode,

            period=period,
            Gap=Gap,
        )

        return result_tmp, result_tmp_gph, table_graph


################################################################################
# 급상승 키워드 선별 함수
def select_keyword(table, today, mode):


    result_tmp, result_tmp_gph, table_graph = prepare_data(table, today, mode)

    # print("result_tmp",result_tmp)
    # print("result_tmp_gph",result_tmp_gph)
    # print("table_graph",table_graph)

    # prepare_data 함수의 반환 값 중 None이 있는지 확인
    if result_tmp is None or result_tmp_gph is None or table_graph is None:


        return None, None, None

    # 데이터프레임의 행 수 확인


    try:

        
        # 검색량 기준
        last = result_tmp.iloc[-1, 0]  # 가장 최근 일자 상대적 검색량
        last_2 = result_tmp.iloc[-2, 0]  # 바로 그 전 일자 상대적 검색량

        # 분산 기준
        var = np.var(result_tmp.iloc[:, 0])

        # 조건 적용 및 분류 로직
        return check_surge_conditions(
            last, last_2, var, result_tmp, result_tmp_gph, table_graph, mode=mode
        )
    except Exception as e:
        # 데이터 처리 중 발생한 예외를 처리
        print(f"An error occurred during keyword selection: {e}")
        return None, None, None


def rising_keyword_analysis(table, today, mode):


    # 모드에 따른 설정값 초기화
    if mode == "daily":
        period_str = "일별"
    elif mode == "weekly":
        period_str = "주별"
        periods = [(0, -1), (-54, -1), (-32, -1)]  # weekly 모드에 맞게 기간 조정
    else:
        period_str = "월별"
        periods = [(0, -1), (-18, -1), (-13, -1)]  # monthly 모드에 맞게 기간 조정

    result_tmp, result_tmp_gph, table_graph = prepare_data(table, today, mode)

    # prepare_data 함수의 결과 검사
    if result_tmp is None or result_tmp_gph is None or table_graph is None:

        return None, None, None

    # 추세 계산 
    top = sloop(result_tmp)
    middle = sloop(result_tmp.iloc[periods[1][0] :,])
    bottom = sloop(result_tmp.iloc[periods[2][0] :,])

    # 최근 값들
    last = result_tmp.iloc[-1, 0]
    last_2 = result_tmp.iloc[-2, 0]

    # 모드에 따른 추가 조건 계산
    recent = (
        sloop(result_tmp.iloc[-3:,])
        if mode != "weekly"
        else sloop(result_tmp.iloc[-4:,])
    )
    recent_2 = (
        sloop(result_tmp.iloc[-5:,])
        if mode != "weekly"
        else sloop(result_tmp.iloc[-7:,])
    )
    recent_3 = (
        sloop(result_tmp.iloc[-8:,]) if mode == "month" else None
    )  # 월별 모드에서만 사용

    # 그래프용 테이블 생성
    result_graph = pd.DataFrame()
    result_graph["검색일자"] = result_tmp_gph.index
    result_graph["기준일자"] = formatted_today
    result_graph["유형"] = f"{period_str}지속상승"
    result_graph["연관검색어"] = result_tmp_gph.columns[0]
    result_graph["검색량"] = result_tmp_gph.values

    # 모드에 따른 조건 검사 및 결과 반환
    if mode == "month":
        if result_tmp is not None and (0 < top) & (0 < middle) & (0 < bottom) & (
            last_2 < last
        ) & (0 < recent < 15) & (-3 < recent_2) & (-3 < recent_3):
            
            print(f"{period_str} 지속상승 키워드 발견 : {result_tmp.columns[0]}")

            return result_tmp.copy(), result_graph, round(top * 100, 2)
    elif mode == "weekly":
        if result_tmp is not None and (0 < top) & (0 < middle) & (0 < bottom) & (
            last_2 < last
        ) & (0 < recent_2 < 10) & (recent < 10):

            print(f"{period_str} 지속상승 키워드 발견 : {table_graph.columns[0]}")
            print(11)
            return result_tmp.copy(), result_graph, round(top * 100, 2)

    return None, None, None


# 상승하는 달 검토하는 함수
# 상승하는 달 검토하는 함수
# 상승하는 달 검토하는 함수

def month_check(table) :

    up_month_list = []

    table_tmp = table.copy()

    table_tmp.loc[:,'year'] = table_tmp.index.year
    table_tmp.loc[:,'month'] = table_tmp.index.month
    sum_table = table_tmp.groupby(['year','month'])[[f'{table.columns[0]}']].sum() # 월별 합계
    sum_table.reset_index(inplace=True)
    sum_table.iloc[:,-1] = sum_table.iloc[:,-1]/sum_table.iloc[:,-1].max() * 100 # 상대적 검색량 변환


    for month in range(1,13) :
        if month != 12 :
            sub_result = sum_table[sum_table['month'] == month].reset_index(drop=True).iloc[:,-1] - sum_table[sum_table['month'] == month+1].reset_index(drop=True).iloc[:,-1]
        else :
            sub_result = sum_table[sum_table['month'] == 12].reset_index(drop=True).iloc[:,-1] - sum_table[sum_table['month'] == 1].reset_index(drop=True).iloc[:,-1]

        if (sub_result[1] * sub_result[2]) > 0 :
            if (sub_result[1]) < 0 :
                if month != 12 :
                    up_month_list.append(month+1)
                else :
                    up_month_list.append(1)
            else :
                pass
        else :
            pass

    return up_month_list

def monthly_rule(table, std_time,mode) :

    today = datetime.now(pytz.timezone('Asia/Seoul'))

    end_time = today - relativedelta(days=1)
    end_time = end_time.strftime("%Y-%m-%d")
    # 시작일자(=3년전)
    start_time = today - relativedelta(years=3) - relativedelta(days=1)
    start_time = start_time.strftime("%Y-%m-%d")

    # 예측을 위한 기간 분리
    end_pred = today
    start_pred = end_pred - relativedelta(years=3)
    end_pred = end_pred.strftime("%Y-%m")
    start_pred = start_pred.strftime("%Y-%m")

    # 분석 기간 설정
    table.index = pd.to_datetime(table.index)
    table_tmp = table[(table.index >= start_time)&(table.index <= end_time)]
    table_pred = table[(table.index >= start_pred)&(table.index < end_pred)]


    # 기간 내 데이터 공백 존재시
    if len(table_tmp.index) < 1080 :
        return None, None, None, None

    # 월별 데이터 테이블로 변환 (36개월)
    tmp_list = []

    for i in range(0,36,1) :
        if i == 0 :
            days_28 = table_tmp.iloc[-(28*(i+1)) : , ].sum()
        else :
            days_28 = table_tmp.iloc[-(28*(i+1)) : -(28*(i)) , ].sum()
        tmp_list.append(days_28)
    tmp_frame = pd.DataFrame(tmp_list)

    r_idx = [i for i in range(tmp_frame.shape[0]-1,-1,-1)]
    result_tmp = pd.DataFrame(tmp_frame, index=r_idx)
    result_tmp.reset_index(drop=True, inplace=True)

    # 기간에 맞춰 상대적 검색량 수정
    result_tmp = result_tmp/result_tmp.max() * 100

    # 인덱스 설정
    result_tmp.index = pd.date_range(end = f'{end_time}', periods = len(result_tmp.index), freq = '28d')

    # 규칙성 검증
    ## 1년씩 확인
    year_1 = result_tmp[:12]   # 최원 1년
    year_1_new = year_1/year_1.max() * 100 # 상대적 변환

    year_2 = result_tmp[12:24]  # 이전 1년
    year_2_new = year_2/year_2.max() * 100 # 상대적 변환

    year_3 = result_tmp[24:36]  # 최근 1년
    year_3_new = year_3/year_3.max() * 100 # 상대적 변환

    dist_1 = dtw(year_1_new,year_2_new,keep_internals=True).distance
    dist_2 = dtw(year_2_new,year_3_new,keep_internals=True).distance
    dist_3 = dtw(year_1_new,year_3_new,keep_internals=True).distance

    var = np.var(result_tmp.iloc[:,0])
    var_1 = np.var(year_1_new.iloc[:,0])
    var_2 = np.var(year_2_new.iloc[:,0])
    var_3 = np.var(year_3_new.iloc[:,0])

    ## 2년씩 확인
    year_4 = result_tmp[:24]
    year_4_new = year_4/year_4.max() * 100

    year_5 = result_tmp[12:36]
    year_5_new = year_5/year_5.max() * 100

    dist_4 = dtw(year_4_new,year_5_new,keep_internals=True).distance

    ## 1. 상승 추세 유무
    total_slop = sloop(result_tmp)

    or_list = [dist_1, dist_2, dist_3]
    new_list = [x for x in or_list if x < 100]
    
    similarity_rt = (1 - (dist_1 + dist_2)/2000) * 100
    similarity_rt = round(similarity_rt,2)

    # 그래프용 테이블 만들기
    result_graph = pd.DataFrame()
    result_graph['검색일자'] = result_tmp.index
    result_graph['기준일자'] = today.strftime("%Y-%m-%d")
    result_graph['유형'] = '월별규칙성'
    result_graph['연관검색어'] = result_tmp.columns[0]
    result_graph['검색량'] = result_tmp.values

    result_graph = result_graph[['기준일자','유형', '연관검색어', '검색일자', '검색량']]

    if len(new_list) >= 2 :
        ### 1번 조건 : 거리가 150보다 작으며, 더 큰 거리가 작은 거리에 비해 2배 미만
        if (max(dist_1, dist_2) < 110.0) & (min(dist_1, dist_2) < 100.0) & (min(dist_1, dist_2) * 2 > max(dist_1, dist_2)) & (dist_4 < 280.0) & (-0.3 < (total_slop) < 0.5):
            print(f'월별 규칙성 키워드 발견 : {result_tmp.columns[0]}')
            table_tmp_2 = result_tmp.copy()

            # 상승하는 달
            rising_month = month_check(table_pred)

            return table_tmp_2 , result_graph, similarity_rt, rising_month

        ### 2번 조건 : 거리가 150보다 하나만 크고, 2년씩 비교한 거리가 300보다 작음
        elif (max(dist_1, dist_2) < 150.0) & (dist_4 < 220.0) & (-0.3 < (total_slop) < 0.5):
            print(f'월별 규칙성 키워드 발견 : {result_tmp.columns[0]}')
            table_tmp_2 = result_tmp.copy()

            # 상승하는 달
            rising_month = month_check(table_pred)

            return table_tmp_2 , result_graph, similarity_rt, rising_month
        else :
            return None, None, None, None
    else :
        return None, None, None, None



    
if __name__ == "__main__":

    BASE_URL = utils.get_secret("BASE_URL")
    CUSTOMER_ID = utils.get_secret("CUSTOMER_ID")
    API_KEY = utils.get_secret("API_KEY")
    SECRET_KEY = utils.get_secret("SECRET_KEY")
    URI = utils.get_secret("URI")
    METHOD = utils.get_secret("METHOD")
    # API 클라이언트 인스턴스 생성
    api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY, URI, METHOD)
    # 검색 기준일
    standard_time = datetime.now()
    params = {
        "search_keywords": [
"상속포기신청","상속등기"

],
        "id": utils.get_secret("clients")["id_1"]["client_id"],
        "pw": utils.get_secret("clients")["id_1"]["client_secret"],
        "api_url": "https://openapi.naver.com/v1/datalab/search",
        "name": "name",
    }

    # api 아이디비번 가져오기
    tasks = []
    # API 요청 URL
    api_url = "https://openapi.naver.com/v1/datalab/search"
    start = time.time()
    clients = utils.get_secret("clients")
    results = asyncio.run(trend_maincode(params, clients, api_url))

    kk = "weekly"

    for df in results:
        # month_a,month_b,month_c,month_d=monthly_rule(df,day,kk)

       # a,b,c,d=monthly_rule(df,day,kk)
        # print(a)
        # print(b)
        # print(c)
        #print(d)
        d, e, f = rising_keyword_analysis(df, day, kk)
        a, b, c = select_keyword(df, day, kk)


    print(time.time() - start)
    # 0.94
    # a,b,c=select_keyword(trend_data,day,a)
    # d,e,f=rising_keyword_analysis(trend_data, day, a)
    # print(d)
    # a,b,c,d=monthly_rule(trend_data,day,kk)
    # a,b,c=select_keyword(trend_data,day,kk)
    # a,b,c=rising_keyword_analysis(trend_data,day,kk)
    # print(a)