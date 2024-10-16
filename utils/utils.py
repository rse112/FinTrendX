import os
import shutil
from datetime import datetime
from pytz import timezone
import json
from typing import Optional
import pandas as pd





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
    """
    Collect keywords data에 대한 고객 정보(ID 및 비밀번호)를 추가합니다.

    이 함수는 각 행에 대해 유니크한 고객 ID와 비밀번호를 할당합니다. 할당은 'clients'에서 가져온 정보를 기반으로 하며,
    각 500개 행마다 새로운 고객 정보를 사용합니다. ID와 비밀번호는 'id'와 'pw' 컬럼으로 추가됩니다.

    Parameters:
    - collected_keywords_data (DataFrame): 고객 정보를 추가할 pandas DataFrame.
      이 데이터프레임은 연관키워드 정보를 담고 있어야 합니다.
    - start_id_index (int, optional): 고객 정보 할당을 시작할 인덱스. 기본값은 1입니다.

    Returns:
    - DataFrame: 고객 ID와 비밀번호가 추가된 데이터프레임.

    Note:
    - 'clients' 정보는 utils.get_secret("clients")를 통해 얻어야 합니다.
    - ID와 PW는 각각 'id', 'pw' 컬럼으로 추가됩니다.
    - 500개 행마다 새로운 고객 정보가 할당되며, 이는 'start_id_index'에 따라 조정됩니다.
    """
    clients = get_secret("clients")
    start_id_index = 1
    clients = get_secret("clients")
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
    """
    주어진 데이터프레임 리스트에서 유효한 데이터프레임들을 결합하고, 각 데이터프레임에 라벨을 추가합니다.

    이 함수는 입력된 데이터프레임 리스트(df_list) 중 None이 아니고, pandas DataFrame 인스턴스이며, 비어있지 않은 데이터프레임을 선별합니다.
    선별된 각 데이터프레임에는 새로운 컬럼 '유형'이 추가되어, 함수에 전달된 라벨 값이 할당됩니다.
    최종적으로, 모든 유효한 데이터프레임들이 단일 데이터프레임으로 결합되어 반환됩니다.

    Parameters:
    - df_list (list): 검사하고 결합할 pandas DataFrame 객체의 리스트.
    - label (str): 각 데이터프레임에 추가될 '유형' 컬럼의 값을 지정하는 문자열.

    Returns:
    - DataFrame: '유형' 컬럼이 추가되고, 입력된 리스트의 유효한 데이터프레임들이 결합된 새로운 DataFrame.
      유효한 데이터프레임이 없을 경우 빈 DataFrame 반환.
    """
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
    """
    주어진 데이터프레임에 대해 각 연관키워드별로 중복되지 않는 검색어 목록을 생성하고 이를 새 컬럼에 할당합니다.

    이 함수는 입력된 collected_keywords_data의 복사본을 생성하고, 각 연관키워드별로 중복되지 않는 검색어를 찾아
    '중복검색어'라는 새 컬럼에 해당 검색어들을 쉼표로 구분된 문자열로 추가합니다. 각 연관키워드에 대해 하나의 '중복검색어' 엔트리가 생성되며,
    이는 해당 연관키워드와 관련된 모든 유니크한 검색어들을 포함합니다.

    Parameters:
    - collected_keywords_data (DataFrame): '연관키워드'와 '검색어' 컬럼을 포함한 pandas DataFrame.

    Returns:
    - DataFrame: 원본 데이터프레임에 '중복검색어' 컬럼이 추가된 새로운 DataFrame. '중복검색어' 컬럼에는
      각 연관키워드에 해당하는 유니크한 검색어 목록(문자열)이 할당됩니다.
    """
    # 1. collected_keywords_data의 복사본 생성
    temp_df = collected_keywords_data.copy()

    # 2. 새로운 컬럼 '중복검색어' 추가 (초기값으로 빈 문자열 할당)
    temp_df["중복검색어"] = ""

    # 3. 연관키워드별로 해당하는 모든 검색어를 찾는 딕셔너리 생성
    keywords_dict = {}
    for index, row in temp_df.iterrows():
        associated_keyword = row["연관키워드"]
        search_keyword = row["검색어"]
        if associated_keyword in keywords_dict:
            # 이미 리스트에 있는 경우 중복을 피하기 위해 추가하지 않음
            if search_keyword not in keywords_dict[associated_keyword]:
                keywords_dict[associated_keyword].append(search_keyword)
        else:
            # 새로운 키워드인 경우 리스트 초기화
            keywords_dict[associated_keyword] = [search_keyword]

    # 4. '중복검색어' 컬럼을 채워 넣음
    for index, row in temp_df.iterrows():
        associated_keyword = row["연관키워드"]
        # 연관키워드에 해당하는 모든 검색어를 '중복검색어' 컬럼에 할당
        temp_df.at[index, "중복검색어"] = ",".join(keywords_dict[associated_keyword])
    return temp_df


def get_top_50_unique_items(collected_keywords_dat_copy, temp_df):

    dict_kind = {}  # 검색 키워드 구분자
    dict_srch = {}  # 연관검색어와 그에 해당한 연관검색어
    dict_rl = {}
    check_list = set()
    keyword_final = load_keywords("main_keyword.json")["keyword_final"]
    for name in keyword_final:

        ceil = 50  # 최대 연관검색어 수

        times = 0

        df_filtered = collected_keywords_dat_copy[
            collected_keywords_dat_copy["검색어"] == name
        ].reset_index(drop=True)
        while times < 50:

            nm = df_filtered.iloc[times]["연관키워드"]

            # 키워드 중복 확인
            while nm in check_list:

                if nm in dict_rl.keys():
                    if str(name) in dict_kind:
                        dict_kind[str(name)].append(str(nm))
                    else:
                        dict_kind[str(name)] = [str(nm)]
                else:
                    pass
                ceil = ceil + 1

                nm = df_filtered["연관키워드"][ceil]

            check_list.add(nm)
            times = times + 1
    # check_list에 해당하는 행을 필터링, '연관키워드' 별로 중복 제거, 인덱스 초기화
    collected_keywords_data = (
        temp_df[temp_df["연관키워드"].isin(check_list)]
        .drop_duplicates(subset="연관키워드", keep="first")
        .reset_index(drop=True)
    )
    return collected_keywords_data, check_list

def generate_result_list(data_table, trend_mapping):
    trend_related_words = {}
    selected_words = []

    for trend_key, trend_value in trend_mapping.items():
        # 필터링된 데이터; 복사 최소화
        filtered_data = data_table[data_table['유형'] == trend_value]
        
        if filtered_data.empty:
            top_search_word = ''
        else:
            sorted_data = filtered_data.sort_values('지표', ascending=False).reset_index(drop=True)
            top_search_word = sorted_data['연관검색어'].iloc[0]
        
        selected_words.append(top_search_word)
        
        # 중복 제거된 연관 검색어 집합
        unique_related_words = set(filtered_data['연관검색어'])
        trend_related_words[trend_value] = list(unique_related_words)
        
    # 딕셔너리에서 DataFrame 생성은 반복문 외부에서 한 번만 수행
    result_dataframe = pd.DataFrame.from_dict(trend_related_words, orient='index').transpose()

    return result_dataframe, selected_words

# trend_type , recent_table,recent_word,yest_table, yest_word
def make_diff(trend_type ,index_names, recent_table,recent_word,yest_table, yest_word):
    
    yesterday_counts = []
    today_counts = []
    absolute_differences = []
    percentage_differences = []
    new_keywords = []
    lost_keywords = []

    iteration_count = len(trend_type)

    for iteration in range(iteration_count):

        # 어제와 오늘 검색어 개수 비교
        yesterday_count = len(yest_table.iloc[:, iteration].dropna(axis=0))
        today_count = len(recent_table.iloc[:, iteration].dropna(axis=0))

        absolute_difference = today_count - yesterday_count
        percentage_difference = 0 if yesterday_count == 0 else round((today_count - yesterday_count) / yesterday_count * 100, 2)

        yesterday_counts.append(yesterday_count)
        today_counts.append(today_count)
        absolute_differences.append(absolute_difference)
        percentage_differences.append(percentage_difference)

        # 검색어 변화 분석
        keywords_yesterday = list(yest_table.iloc[:, iteration].dropna(axis=0))
        keywords_today = list(recent_table.iloc[:, iteration].dropna(axis=0))

        new_keywords_list = list(set(keywords_today) - set(keywords_yesterday))
        lost_keywords_list = list(set(keywords_yesterday) - set(keywords_today))

        new_keywords.append(new_keywords_list)
        lost_keywords.append(lost_keywords_list)

    # 결과 데이터프레임 생성
    diff_summary = dict(zip(index_names, [yesterday_counts, today_counts, absolute_differences, percentage_differences, new_keywords, lost_keywords, recent_word]))
    diff_table = pd.DataFrame.from_dict(diff_summary, columns=trend_type.values(), orient='index')

    # 리스트를 문자열로 변환
    for col in range(len(diff_table.columns)):
        diff_table.iloc[4, col] = str(diff_table.iloc[4, col]).replace('[', '').replace(']', '')
        diff_table.iloc[5, col] = str(diff_table.iloc[5, col]).replace('[', '').replace(']', '')
    return diff_table




# 전송용 결과 테이블 생성 함수


def make_csv(table):

    # 컬럼 추출
    col_a = ""
    col_b = ""

    for col in table.columns:
        col_a = str(col) + "|||"
        col_b = col_b + col_a
    col_b

    # 행 추출
    row_list = []

    for j in range(0, len(table)):
        tmp_a = ""
        tmp_b = ""

        for i in range(0, len(table.columns)):
            tmp_a = str(table.iloc[j, i]) + "|||"
            tmp_b = tmp_b + tmp_a
        row_list.append(tmp_b)

    row_list.insert(0, col_b)
    df = pd.DataFrame(row_list)

    return df


def find_latest_date_before_today(result_out_path):
    '''
    모니터링을 위한 폴더를 찾고 가장 최근 날짜를 반환합니다.
    '''
    # 'result_out' 폴더 내의 모든 서브폴더를 리스트로 가져오기
    folder_names = [name for name in os.listdir(result_out_path) if os.path.isdir(os.path.join(result_out_path, name))]

    # 오늘 날짜 설정 (시간 부분 제거)
    today = datetime.now().date()
    date_format = '%y%m%d'

    # 날짜 포맷에 맞게 변환하고, 오늘 날짜 이전인 폴더만 필터링
    valid_dates = []
    for folder_name in folder_names:
        try:
            folder_date = datetime.strptime(folder_name, date_format).date()  # 시간 부분 제거
            if folder_date < today:
                valid_dates.append(folder_date)
        except ValueError:
            # 폴더 이름이 날짜 형식에 맞지 않는 경우 무시
            continue

    # 오늘 날짜 이전의 가장 최근 날짜 찾기
    if valid_dates:
        latest_date = max(valid_dates)
        formatted_latest_date = latest_date.strftime(date_format)
        return formatted_latest_date
    else:
        return None
    

if __name__ == "__main__":
    keywords = load_keywords("main_keyword.json")
    print(type(keywords["keyword_final"]))
    a, b = get_today_date()
    print(a)
