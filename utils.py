import os
import shutil
from datetime import datetime
from pytz import timezone
import json
from typing import Optional
import pandas as pd
import utils


def merge_and_mark_duplicates_limited(df_list):
    """
    여러 DataFrame을 병합하고, '연관키워드'가 중복되는 경우 '중복검색어' 컬럼에 해당하는 모든 '검색어'를 마킹합니다.
    이 함수는 df_list에서 제공된 모든 DataFrame의 처음 50개 행에 대해 이 작업을 수행합니다.

    Parameters:
    - df_list: DataFrame 객체의 리스트

    Returns:
    - DataFrame: 병합 및 처리된 데이터프레임의 처음 50개 행
    """
    df_combined = pd.DataFrame()
    # 각 DataFrame의 처음 50개 행만 사용
    limited_dfs = [df.iloc[50:100] for df in df_list]

    # 제한된 DataFrame들을 합침
    df_combined = pd.concat(limited_dfs)
    # '연관키워드'로 그룹화 후, 각 그룹의 '검색어'를 합쳐서 '중복검색어' 컬럼 생성
    df_combined["중복검색어"] = df_combined.groupby("연관키워드")["검색어"].transform(
        lambda x: ",".join(x.unique())
    )

    # 중복 제거 (첫 번째 등장을 제외한 동일 '연관키워드' 삭제)
    df_combined.drop_duplicates(subset="연관키워드", inplace=True)

    # 인덱스 리셋
    df_combined.reset_index(drop=True, inplace=True)

    return df_combined


def get_secret(
    key: str, default_value: Optional[str] = None, json_path: str = "secrets.json"
) -> str:
    """
    지정된 JSON 파일에서 키에 해당하는 비밀 값을 검색합니다.

    이 함수는 주어진 키를 사용하여 JSON 파일에서 비밀 값을 찾고, 해당 키가 없을 경우 기본 값을 반환하거나 환경 변수가 설정되지 않았음을 알리는 예외를 발생시킵니다.

    매개변수:
    - key (str): 검색할 비밀 값의 키입니다.
    - default_value (Optional[str]): 키가 없을 경우 반환될 기본 값입니다. 기본값은 None입니다.
    - json_path (str): 비밀 값을 포함하고 있는 JSON 파일의 경로입니다. 기본값은 "secrets.json"입니다.

    반환값:
    - str: 검색된 비밀 값 또는 기본 값입니다.

    예외:
    - EnvironmentError: 주어진 키에 해당하는 비밀 값이 없고 기본 값도 제공되지 않았을 때 발생합니다.
    """
    with open(json_path, encoding="utf-8") as f:
        secrets = json.loads(f.read())
    try:
        return secrets[key]
    except KeyError:
        if default_value is not None:
            return default_value
        raise EnvironmentError(f"Set the {key} environment variable.")


def load_keywords(filename):
    """
    지정된 파일명의 JSON 파일로부터 키워드를 로드합니다.

    이 함수는 주어진 파일명에 해당하는 JSON 파일을 열고, 파일 내용을 파싱하여 Python 객체로 변환합니다.
    반환된 객체는 일반적으로 문자열의 리스트이며, 이 리스트는 JSON 파일 내에 정의된 키워드들을 포함합니다.

    :param filename: 읽을 JSON 파일의 경로와 파일명을 포함하는 문자열


    :return: JSON 파일 내용을 담고 있는 Python 객체 (보통 리스트)
    """
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def make_directory(path):
    """
    주어진 경로에 디렉토리(폴더)를 생성합니다. 이미 해당 경로에 디렉토리가 존재하는 경우, 추가적인 액션은 취해지지 않습니다.

    이 함수는 os.makedirs 함수를 사용하여 경로를 생성합니다. `exist_ok=True` 매개변수는 경로가 이미 존재하는 경우
    오류를 발생시키지 않고 넘어가도록 합니다.

    :param path: 생성할 디렉토리의 경로
    """
    os.makedirs(path, exist_ok=True)


def get_today_date():
    """
    현재 날짜와 시간을 'Asia/Seoul' 타임존 기준으로 설정하고,
    'YYYY-MM-DD' 형식의 문자열로 반환합니다. 또한,
    'YYMMDD' 형식의 문자열도 함께 반환합니다.

    :return: 오늘 날짜('YYYY-MM-DD' 형식), 'YYMMDD' 형식의 날짜 문자열
    """
    today = datetime.now(timezone("Asia/Seoul"))
    formatted_today = today.strftime("%Y-%m-%d")
    day = today.strftime("%y%m%d")
    return formatted_today, day


def process_data(data, condition, type_label, data_lists):
    """
    지정된 조건에 따라 데이터를 필터링하고, 추가 처리를 통해 최종 데이터프레임을 반환하는 함수.

    Parameters:
    - data (pd.DataFrame): 원본 데이터프레임.
    - condition (str): 필터링할 조건의 컬럼명.
    - type_label (str): 필터링된 데이터에 적용할 '유형'의 라벨.
    - data_lists (list): '지표' 열에 채울 데이터를 포함하는 데이터프레임 리스트.

    Returns:
    - pd.DataFrame: 처리된 최종 데이터프레임.
    """
    # 조건에 맞는 데이터 필터링
    filtered_data = data[data[condition] == 1].copy()
    filtered_data["유형"] = type_label

    # 불필요한 열 삭제
    columns_to_drop = [
        "일별급상승",
        "주별급상승",
        "월별급상승",
        "주별지속상승",
        "월별지속상승",
        "월별규칙성",
        "id",
        "pw",
        "검색어",
    ]
    filtered_data.drop(columns_to_drop, axis=1, inplace=True)

    # 인덱스 재설정
    filtered_data.reset_index(drop=True, inplace=True)

    # '지표' 열 초기화
    filtered_data["지표"] = None

    for df in data_lists:
        for index, row in filtered_data.iterrows():
            # 현재 행의 '연관검색어'와 일치하는 data_list의 데이터프레임 내의 '연관검색어' 찾기
            matching_info_data = df[df["연관검색어"] == row["연관키워드"]][
                "InfoData"
            ].unique()
            if len(matching_info_data) > 0:
                # 일치하는 'InfoData' 값이 있으면, 첫 번째 값을 '지표' 열에 할당
                filtered_data.at[index, "지표"] = str(matching_info_data[0]) + "%"

    # '상승월' 열 추가
    filtered_data["상승월"] = None  

    return filtered_data


def update_keywords_flag(dataframe, data_list, flag_name):
    """
    주어진 데이터프레임에, 데이터 리스트에 따라 특정 플래그를 설정하는 함수.

    Parameters:
    - dataframe (pd.DataFrame): 업데이트할 데이터프레임.
    - data_list (list of pd.DataFrame): 연관 검색어가 포함된 데이터프레임 리스트.
    - flag_name (str): 데이터프레임에 설정할 플래그의 이름.

    Returns:
    None. 함수는 입력된 데이터프레임을 직접 수정합니다.
    """
    unique_associated_keywords = set()
    for df in data_list:
        unique_associated_keywords.update(df["연관검색어"].unique())
    for index, row in dataframe.iterrows():
        if row["연관키워드"] in unique_associated_keywords:
            dataframe.at[index, flag_name] = 1


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


def process_and_concat(df_list, label):
    # 여기서 df_list는 데이터 프레임의 리스트를 기대함
    valid_dfs = [
        df
        for df in df_list
        if df is not None and isinstance(df, pd.DataFrame) and not df.empty
    ]
    if not valid_dfs:  # 유효한 DataFrame이 없으면 빈 DataFrame 반환
        return pd.DataFrame()
    for df in valid_dfs:
        df["유형"] = label
    return pd.concat(valid_dfs).reset_index(drop=True)



def generate_unique_search_terms(collected_keywords_data):
    # 1. collected_keywords_data의 복사본 생성
    temp_df = collected_keywords_data.copy()

    # 2. 새로운 컬럼 '중복검색어' 추가 (초기값으로 빈 문자열 할당)
    temp_df['중복검색어'] = ''

    # 3. 연관키워드별로 해당하는 모든 검색어를 찾는 딕셔너리 생성
    keywords_dict = {}
    for index, row in temp_df.iterrows():
        associated_keyword = row['연관키워드']
        search_keyword = row['검색어']
        if associated_keyword in keywords_dict:
            # 이미 리스트에 있는 경우 중복을 피하기 위해 추가하지 않음
            if search_keyword not in keywords_dict[associated_keyword]:
                keywords_dict[associated_keyword].append(search_keyword)
        else:
            # 새로운 키워드인 경우 리스트 초기화
            keywords_dict[associated_keyword] = [search_keyword]

    # 4. '중복검색어' 컬럼을 채워 넣음
    for index, row in temp_df.iterrows():
        associated_keyword = row['연관키워드']
        # 연관키워드에 해당하는 모든 검색어를 '중복검색어' 컬럼에 할당
        temp_df.at[index, '중복검색어'] = ','.join(keywords_dict[associated_keyword])
    return temp_df





def get_top_50_unique_items(collected_keywords_dat_copy,temp_df):
    dict_kind = {}  # 검색 키워드 구분자
    dict_srch = {}  # 연관검색어와 그에 해당한 연관검색어
    dict_rl = {} 
    check_list=set()

    keyword_final = ['주식', '금리', '금융상품', '디지털자산', '부동산', '세금', '재테크', '돈버는법', '테마주', '특징주', '외국인순매수', '신규상장', '급등주', '공모주',
                        '배당주', '미국주식', '주가지수', 'WTI', '금값', '채권금리', '달러환율', '미국금리',
                        'ETF', '중개형ISA', '적립식펀드', '개인연금', '퇴직연금', 'ELS', 'CMA통장', 'CMA금리비교', '채권', '신탁', 'RP', '암호화폐', '미술품', '조각투자', 
                        '아파트청약', '리워드', '캐시백', '돈버는앱', '건강보험', '자동차보험', '의료비보험', '상속', '증여']
    for name in keyword_final :

        ceil = 50 # 최대 연관검색어 수

        times = 0

        df_filtered = collected_keywords_dat_copy[collected_keywords_dat_copy['검색어'] == name].reset_index(drop=True)
        while times < 50 :
            
            nm = df_filtered.iloc[times]['연관키워드']

            
            # 키워드 중복 확인
            while nm in check_list :

                if nm in dict_rl.keys() :
                    if str(name) in dict_kind :
                        dict_kind[str(name)].append(str(nm))
                    else :
                        dict_kind[str(name)] = [str(nm)]
                else :
                    pass
                ceil = ceil + 1

                nm = df_filtered['연관키워드'][ceil]
            
            check_list.add(nm)
            times = times + 1
    # check_list에 해당하는 행을 필터링, '연관키워드' 별로 중복 제거, 인덱스 초기화
    collected_keywords_data = temp_df[temp_df['연관키워드'].isin(check_list)] \
                                .drop_duplicates(subset='연관키워드', keep='first') \
                                .reset_index(drop=True)
    return collected_keywords_data,check_list




if __name__ == "__main__":
    keywords = load_keywords("secrets.json")
    print(keywords["clients"]["id_1"]["client_id"])
    a, b = get_today_date()
    print(a)
