
from datetime import datetime
import pandas as pd
def format_info_data(info_result_final,final_merged_df_copy):
    # 최종 DataFrame 확인
    final_merged_df_result = pd.merge(info_result_final, final_merged_df_copy, how='left', on='연관검색어')
    today_date = datetime.now().strftime("%Y-%m-%d")

    # '기준일자' 컬럼을 가장 앞에 추가
    final_merged_df_result.insert(0, '기준일자', today_date)
    # 컬럼명 변경: '중복검색어' -> '검색키워드', '월간검색수_합계' -> '검색량'

    final_merged_df_result.rename(columns={'중복검색어': '검색키워드', '월간검색수_합계': '검색량'}, inplace=True)

    final_merged_df_result = final_merged_df_result.drop(columns=["검색어"])


    final_merged_df_result['상승월'] = None



    # 형식맞추기 위한 info_result_final 순서 정렬
    info_result_af_copy=pd.DataFrame()
    a = final_merged_df_result.query("`유형` == '일별 급상승'")
    b = final_merged_df_result.query("`유형` == '주별 급상승' or `유형` == '주별 지속상승'")
    c = final_merged_df_result.query("`유형` == '월별 급상승' or `유형` == '월별 지속상승' or `유형` == '월별 규칙성'")
    a_sort=a.sort_values(by=['연관검색어', '유형'], ascending=[True, True])
    b_sort = b.sort_values(by=['연관검색어', '유형'], ascending=[True, True])
    c_sort = c.sort_values(by=['연관검색어', '유형'], ascending=[True, True])
    info_result_af_copy=pd.concat([a_sort,b_sort,c_sort])

    # 형식을 위한 이름 변경
    new_column_order = ['기준일자', '유형', '연관검색어', '검색키워드', '검색량', '지표', '뉴스제목', '뉴스링크', '활동성', '구글검색어', '네이버검색어', '상승월']
    info_result_af_copy_reordered = info_result_af_copy[new_column_order]
    ################################
    # 유형 순서 정렬
    info_result_af_copy_reordered_modified = info_result_af_copy_reordered.copy()


    # 인덱스 재설정
    info_result_af_copy_reordered_modified.reset_index(drop=True, inplace=True)

    sort_order = {
        "일별 급상승": 1,
        "주별 급상승": 2,
        "주별 지속상승": 3,
        "월별 급상승": 4,
        "월별 지속상승": 5,
        "월별 규칙성" : 6
    }

    # 유형 컬럼에 대한 정렬 순서를 적용하기 위해 임시 컬럼 추가
    info_result_af_copy_reordered_modified['sort_key'] = info_result_af_copy_reordered_modified['유형'].map(sort_order)

    # 임시 컬럼을 기준으로 정렬
    info_result_af_copy_reordered_modified = info_result_af_copy_reordered_modified.sort_values(by=['sort_key', '연관검색어'], ascending=[True, True])

    # 임시 컬럼 삭제
    info_result_af_copy_reordered_modified.drop('sort_key', axis=1, inplace=True)

    info_result_af_copy_reordered_modified.reset_index(drop=True, inplace=True)
    return info_result_af_copy_reordered_modified




###
def split_df_by_type(df, type_names):
    """
    유형별로 데이터프레임을 분리하고 정렬합니다.
    여러 유형을 리스트로 받아 해당 유형에 맞는 데이터프레임을 반환합니다.
    """
    if not isinstance(type_names, list):
        type_names = [type_names]
    
    filtered_dfs = []
    for type_name in type_names:
        filtered_df = df[df['유형'] == type_name]
        if not filtered_df.empty:
            filtered_df = filtered_df.sort_values(by=['연관검색어', '유형', '검색일자'])
            filtered_dfs.append(filtered_df)
    
    if filtered_dfs:
        return pd.concat(filtered_dfs).reset_index(drop=True)
    else:
        return pd.DataFrame()


def process_monthly_pattern(df):
    """'월별 규칙성' 데이터 처리"""
    df['상승월'] = df['상승월'].apply(lambda x: None if x == ' ' else x)
    return df

def clean_up_info_data(info_data):
    """info_data 데이터프레임 정리"""
    info_data['상승월'] = info_data['상승월'].str.replace(' ', '').replace('0.0', ' ')
    
    # 문자열이 아니거나, None인 경우 처리를 추가
    info_data['상승월'] = info_data['상승월'].apply(
        lambda x: str(int(float(x))) if isinstance(x, str) and x.replace('.', '', 1).isdigit() else x
    )
    return info_data


def format_result(graph_result, info_result_af_copy_reordered_modified):
    replace_values = {
    '일별 급상승': '일별급상승',
    '주별 급상승': '주별급상승',
    '주별 지속상승': '주별지속상승',
    '월별 급상승': '월별급상승',
    '월별 지속상승': '월별지속상승',
    '월별 규칙성': '월별규칙성'
    }

    # '월별 규칙성'을 제외한 모든 유형 처리
    df_without_monthly_pattern = info_result_af_copy_reordered_modified[info_result_af_copy_reordered_modified['유형'] != '월별 규칙성'].copy()
    monthly_pattern_df = process_monthly_pattern(info_result_af_copy_reordered_modified[info_result_af_copy_reordered_modified['유형'] == '월별 규칙성'].copy())

    # 형식에 맞춰서 데이터 처리
    graph_result['유형'] = graph_result['유형'].replace(replace_values)
    
    # 검색량이 NA인 연관검색어 제외
    na_terms = graph_result[pd.isna(graph_result['검색량'])]['연관검색어'].unique()
    filtered_graph_result = graph_result[~graph_result['연관검색어'].isin(na_terms)]
    
    # 유형별로 데이터프레임 분리 및 정렬
    daily_rise = split_df_by_type(filtered_graph_result, ['일별급상승'])

    # 월별급상승, 월별지속상승, 월별규칙성에 대한 처리
    weekly_monthly_rise = split_df_by_type(filtered_graph_result, ['월별급상승', '월별지속상승', '월별규칙성'])

    # 주별급상승, 주별지속상승에 대한 처리
    weekly_rise = split_df_by_type(filtered_graph_result, ['주별급상승', '주별지속상승'])

    # 데이터프레임 결합
    combined_df = pd.concat([daily_rise, weekly_rise, weekly_monthly_rise]).reset_index(drop=True)

    # info_data 처리
    info_data = clean_up_info_data(pd.concat([df_without_monthly_pattern, monthly_pattern_df]).reset_index(drop=True))

    return combined_df, info_data

def update_rising_months(info_df, graph_df):
    """
    info_df의 '상승월' 열을 graph_df 데이터를 기반으로 업데이트합니다.
    """
    for index, row in info_df.iterrows():
        # graph_df에서 일치하는 '연관검색어'와 '유형'이 '월별규칙성'인 행 찾기
        matching_rows = graph_df[(graph_df['연관검색어'] == row['연관검색어']) & (graph_df['유형'] == '월별규칙성')]
        
        # 일치하는 행들의 'RisingMonth' 값들을 리스트로 가져오기
        if not matching_rows.empty:
            rising_months_list = matching_rows['RisingMonth'].tolist()
            # '상승월' 열에 값 할당
            info_df.at[index, '상승월'] = ', '.join(map(str, rising_months_list))
            
    return info_df


def data_merge(news_data,collected_keywords_dat_copy,directory_path,info_result_final,rising_keywords_results):
    name_list = list(news_data.keys())  
    # DataFrame 초기화
    news_df = pd.DataFrame()

    # 모든 키워드에 대해 처리
    for keyword in name_list:
        # 뉴스 항목이 있는 경우 데이터 추가
        for news_item in news_data[keyword]:
            news_row = [keyword, news_item[0], news_item[1]]  # 연관키워드, 뉴스제목, 뉴스링크
            news_df = pd.concat([news_df, pd.DataFrame([news_row])], ignore_index=True)

        # 뉴스 항목 수가 10개에 미치지 못하면 나머지를 빈 행으로 채움
        for _ in range(10 - len(news_data[keyword])):
            empty_row = [keyword, None, None]  # 연관키워드, 빈 뉴스제목, 빈 뉴스링크
            news_df = pd.concat([news_df, pd.DataFrame([empty_row])], ignore_index=True)

    # 칼럼 이름 설정
    news_df.columns = ['연관검색어', '뉴스제목', '뉴스링크']

    keyword_activity_rates = pd.read_csv(f'{directory_path}/keyword_activity_rates.csv')
    keyword_activity_rates.columns = ['연관검색어', '활동성']

    # '활동성' 열의 데이터를 백분율 형태의 문자열로 변환
    keyword_activity_rates['활동성'] = keyword_activity_rates['활동성'].apply(lambda x: f"{x}%")
    # news_df와 keyword_activity_rates를 '연관검색어' 열을 기준으로 병합
    keyword_activity_rates = keyword_activity_rates.drop_duplicates(subset=['연관검색어'])
    merged_keyword_activity_rates = pd.merge(news_df, keyword_activity_rates, on='연관검색어', how='left')




    ####
    # 네이버 merge
    ####
    collected_keywords_dat_copy.rename(columns={'연관키워드': '연관검색어'}, inplace=True)
    info_result_final.rename(columns={'연관키워드': '연관검색어'}, inplace=True)
    collected_keywords_dat_copyy=collected_keywords_dat_copy.copy()
    # collected_keywords_dat_copy에서 '연관키워드'와 '검색어'를 기준으로 중복 제거
    collected_keywords_dat_copy = collected_keywords_dat_copy.drop_duplicates(subset=['연관검색어'], keep='first')
    # 이제 merged_keyword_activity_rates와 결합
    final_merged_df = pd.merge(merged_keyword_activity_rates, collected_keywords_dat_copy[['연관검색어', '검색어']], on='연관검색어', how='left')
    final_merged_df_copy = final_merged_df.copy()

    # 구글검색어 컬럼을 초기화합니다.
    final_merged_df_copy['구글검색어'] = None

    # 이후의 모든 작업은 final_merged_df_copy에 대해 수행합니다.
    i = 0
    for keyword, queries in rising_keywords_results.items():
        filled_queries = queries[:10] + [None] * (10 - len(queries[:10]))
        for query in filled_queries:
            if i < len(final_merged_df_copy):
                final_merged_df_copy.at[i, '구글검색어'] = query
                i += 1
            else:
                break


    # final_merged_df의 '검색어' 컬럼에서 각 10번째 검색어를 추출합니다.
    keyword_list_per_10 = final_merged_df_copy['검색어'].tolist()[::10]


    
    # collected_keywords_dat_copy에서 각 검색어별 상위 10개 연관검색어를 가져옵니다.
    top_keywords_by_search = collected_keywords_dat_copyy.groupby('검색어').apply(
        lambda x: x.nlargest(10, '월간검색수_합계')
    ).reset_index(drop=True)



    # 새로운 DataFrame을 초기화합니다. 이 DataFrame에는 각 검색어별 상위 10개 연관검색어가 포함됩니다.
    new_rows_for_final_df = []


    for keyword in keyword_list_per_10:
        # 특정 키워드에 대한 상위 10개 연관 검색어 추출
        top_queries_for_keyword = top_keywords_by_search[top_keywords_by_search['검색어'] == keyword].head(10)
        
        # 추출된 연관 검색어를 결과 리스트에 추가
        num_rows_added = 0  # 추가된 연관 검색어의 수를 추적
        for _, row in top_queries_for_keyword.iterrows():
            new_rows_for_final_df.append(row['연관검색어'])
            num_rows_added += 1
        
        # 10개 미만인 경우 나머지를 None으로 채우기
        for _ in range(10 - num_rows_added):
            new_rows_for_final_df.append(None)

    if len(new_rows_for_final_df) == len(final_merged_df_copy):
        final_merged_df_copy['네이버검색어'] = new_rows_for_final_df
    else:
        print("경고: '네이버검색어' 데이터의 길이가 final_merged_df와 다릅니다. 데이터 확인이 필요합니다.")
    return info_result_final,final_merged_df_copy

def format_main(news_data,collected_keywords_dat_copy,directory_path,info_result_final,rising_keywords_results,graph_result):
    info_result_final,final_merged_df_copy = data_merge(news_data,collected_keywords_dat_copy,directory_path,info_result_final,rising_keywords_results)
    print("data_merge함수가 실행완료했습니다.")
    info_result_af_copy_reordered_modified = format_info_data(info_result_final,final_merged_df_copy)
    print("format_info_data함수가 실행완료했습니다.")
    info_result_af_copy_reordered_modified=update_rising_months(info_result_af_copy_reordered_modified, graph_result)
    print("update_rising_months함수가 실행완료했습니다.")
    combined_df,info_data=format_result(graph_result, info_result_af_copy_reordered_modified)
    print("format_result함수가 실행완료했습니다.")
    print(" 형식 맞추기 완료했습니다.")
    return combined_df,info_data