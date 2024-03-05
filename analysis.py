# import pandas as pd
# import utils
# import trend as trend
# def update_search_volumes(trend_analysis_df, related_keywords_table, category_dict, search_volume_dict, search_keyword, analysis_info, info_dict):
#     if trend_analysis_df is None or '연관검색어' not in trend_analysis_df.columns or trend_analysis_df['연관검색어'].empty:
#         return

#     # 업데이트: 키워드 카테고리와 관련 검색어 볼륨
#     first_related_keyword = trend_analysis_df['연관검색어'].iloc[0]
#     if search_keyword in category_dict:
#         category_dict[search_keyword].append(first_related_keyword)
#     else:
#         category_dict[search_keyword] = [first_related_keyword]

#     if '연관키워드' not in related_keywords_table.columns:
#         print("'연관키워드' 컬럼이 related_keywords_table에 존재하지 않습니다.")
#         return

#     # 연관키워드에 대한 월간검색수_합계 가져오기 및 info_dict 업데이트
#     related_row = related_keywords_table[related_keywords_table['연관키워드'] == first_related_keyword]
#     if not related_row.empty:
#         search_volume_dict[first_related_keyword] = related_row['월간검색수_합계'].values[0]
#         # 여기에서 '연관검색어의 첫 번째 값에 대한 추가 정보'를 업데이트합니다.
#         info_dict[first_related_keyword] = analysis_info
#     else:
#         print(f"'{first_related_keyword}'에 대한 월간검색수_합계 정보가 없습니다.")





# def check_result(**kwargs):

#     # 추출: 결과 데이터프레임과 그래프 데이터프레임, 분석 정보, 관련 검색어 정보
#     trend_analysis_df = kwargs.get('tmp')
#     graph_data_df = kwargs.get('tmp_gph')
#     analysis_info = kwargs.get('tmp_info')
#     trend_df = kwargs.get('trend_df')
#     graph_df = kwargs.get('graph_df')
#     search_keyword = kwargs.get('keywordName')
#     category_dict = kwargs.get('keyword_categories')
#     search_volume_dict = kwargs.get('related_search_volume')
#     related_keywords_table = kwargs.get('df_table')
#     info_dict = kwargs.get('info_dict')
#     related_search_terms = kwargs.get('related_search_terms')
    
#         #검색어와 연관 검색어의 검색 볼륨을 업데이트합니다.
#     update_search_volumes(trend_analysis_df, related_keywords_table, category_dict, search_volume_dict, search_keyword, analysis_info, info_dict)



#     related_search_terms[search_keyword] = related_keywords_table['연관키워드'][:10].to_list()

#             # 데이터프레임 업데이트
#     trend_df = pd.concat([trend_df, trend_analysis_df], axis=1)
#     graph_df = pd.concat([graph_df, graph_data_df], axis=0)

#     return category_dict, search_volume_dict, info_dict, related_search_terms, trend_df, graph_df


# def handle_api_call(keywordName, currentRequestCount, 
#                             df_table, clients, apiCallCount, 
#                             current_client_index, request_limit, api_url):
    
#     '''
    
#     '''
#     if apiCallCount <= request_limit:
#         # 현재 클라이언트 정보 가져오기
#         client_id, client_secret, client_index = utils.get_client_info(clients, current_client_index)
#         real_client_id = clients[client_id]['client_id']

#         # 로깅
#         utils.log_progress(keywordName, currentRequestCount, len(df_table), client_id, apiCallCount, request_limit)
        
#         # 관련 키워드 추출
#         related_keyword = df_table['연관키워드'][currentRequestCount]

#         # API 요청 데이터 준비
#         request_data = {
#             'keywordName': keywordName,
#             'search_keyword': related_keyword,
#             'client_id': real_client_id,
#             'client_secret': client_secret,
#             'api_url': api_url
#         }

#         # API 요청 데이터를 DataFrame에 추가
#         return request_data, apiCallCount + 1, current_client_index
#     else:
#         # 요청 한도 초과 시 클라이언트 인덱스 업데이트
#         current_client_index += 1
#         if current_client_index >= len(clients):
#             print("모든 API 클라이언트의 요청 한도 초과")
#             return None, apiCallCount, current_client_index  # 처리 중단을 위한 None 반환
#         else:
#             # 클라이언트 전환 후 재시도
#             return handle_api_call(keywordName, currentRequestCount, df_table, clients, 1, current_client_index, request_limit, api_url)



# # 데이터 규격화 함수
# def map_columns_based_on_keys(review_types, mode):
#     # 'mode' 키와 'trend_df'가 존재하며, 해당 'trend_df' 값이 None이 아닌지 확인
#     if mode in review_types and review_types[mode].get('trend_df') is not None:
#         trend_df = review_types[mode]['trend_df']
        
#         # 필요한 컬럼이 trend_df에 존재하는지 확인
#         required_columns = ['검색일자', '연관검색어', '검색량']
#         if not all(column in trend_df.columns for column in required_columns):
#             # 필요한 컬럼이 없는 경우 예외 처리
#             print(f"One or more required columns {required_columns} are missing in the DataFrame.")
#             return None
        
#         # 필요한 컬럼만 선택하여 새로운 DataFrame 생성
#         final_df = trend_df[required_columns].copy()
#         a = final_df.iloc[:, 0].tolist()
#         final_dff = final_df[['검색량']].copy()
#         final_dff.insert(0, '검색일자', a)
#         keys_list = list(review_types[mode]['info_dict'].keys())
        
#         # '검색일자' 컬럼을 포함하고, 나머지 컬럼에 keys_list의 키들을 매핑하기 위한 새 컬럼 이름 리스트 생성
#         new_column_names = ['검색일자'] + keys_list
#         final_dff.columns = new_column_names
#         return final_dff
#     else:
#         # trend_df가 None인 경우 또는 mode 키가 존재하지 않는 경우 예외 처리
#         print(f"The 'trend_df' for mode '{mode}' is None or the mode does not exist.")
#         return None
    


# def analyze_trend_data(api_request_data,keywordName,standard_time,review_types,up_month,day,df_table,keyword_categories,\
#                        related_search_volume,related_search_terms):    
#     unique_api_request_data  = api_request_data.drop_duplicates(subset=['search_keyword'])
#     print(f'유일한 API 요청 데이터 수: {len(unique_api_request_data)}')
#     for index, row in unique_api_request_data.iterrows():
#         if row['keywordName'] != keywordName:
#             continue

            
#         trend_data = trend.trend_load(standard_time, row['search_keyword'], row['client_id'], row['client_secret'], row['api_url'])

#         for review_key, settings in review_types.items():
#                 # 'monthly_rule' 유형의 처리를 먼저 확인
#             if review_key == 'monthly_rule':
#                 tmp, tmp_gph, tmp_info, rising_month = settings['function'](trend_data, day, settings['time_period'])
#                     # row[search_keyword] : 해당 키워드의 연관키워드 리스트
#                 if tmp is not None:
#                     if str(keywordName) not in up_month:
#                         up_month[str(keywordName)] = rising_month
#                 continue
                
#                 # 나머지 유형의 일반적인 처리
#             tmp, tmp_gph, tmp_info = settings['function'](trend_data, day, settings['time_period'])

#             if tmp is None:
#                 continue

#                 # 결과 처리 로직에 사용될 인자들을 하나의 딕셔너리로 묶기
#             check_result_args = {
#                 'tmp': tmp,
#                 'tmp_gph': tmp_gph,
#                 'tmp_info': tmp_info,
#                 'trend_df': settings['trend_df'],
#                 'graph_df': settings['graph_df'],
#                 'keywordName': keywordName,
#                 'keyword_categories': keyword_categories,
#                 'related_search_volume': related_search_volume,
#                 'df_table': df_table,
#                 'info_dict': settings['info_dict'],
#                 'related_search_terms': related_search_terms,
#                     # 'currentKeywordData',: row['search_keyword']
#             }
    
#                 # **kwargs를 사용하여 딕셔너리를 함수에 전달
#             keyword_categories, related_search_volume, settings['info_dict'], related_search_terms, settings['trend_df'], settings['graph_df'] = check_result(**check_result_args)
#     return keyword_categories,related_search_volume,related_search_terms,up_month,review_types



# def collect_and_analyze_keyword_trends(keywords,state,day,total_keywords,\
#                                        clients,request_limit,api_url,standard_time,review_types,up_month,apiCallCount,current_client_index,i,api_request_data,\
#                                         keyword_categories,related_search_volume,related_search_terms):
    

#     for keywordName   in keywords[state['keyword_index']:]:
#             df_table = pd.read_csv('./data/rl_srch/' + str(day) + f'/{keywordName}.csv', encoding='euc-kr')
#             print(f'################################################ {keywordName } ({i+1}/{total_keywords}) ################################################')
#             maxKeyword = min(50, len(df_table))   # 최대 연관검색어 수 (50개가 안되면 DF_TABLE의 길이만큼)

#             for currentRequestCount  in range(state['currentRequestCount_index'], maxKeyword):
#                 # 설명

#                 request_data, apiCallCount, current_client_index = handle_api_call(
#                     keywordName, currentRequestCount, df_table, clients, apiCallCount, 
#                     current_client_index, request_limit, api_url)

#                 if request_data is not None:
#                     # 데이터 프레임에 API 요청 데이터 추가
#                     new_row = pd.DataFrame([request_data])
#                     api_request_data = pd.concat([api_request_data, new_row], ignore_index=True)
#                 else:
#                     # API 요청 한도 초과 시 처리
#                     break

#             if current_client_index >= len(clients):
#                 print("모든 API 클라이언트의 요청 한도 초과")
#                 break

#             i += 1 
#             print(f'API 요청 데이터 수: {len(api_request_data)}')


#             keyword_categories,related_search_volume,related_search_terms,up_month,review_types\
#                 =analyze_trend_data(api_request_data,keywordName,standard_time,review_types,up_month,day,df_table,keyword_categories,\
#                        related_search_volume,related_search_terms)
            

#     return keyword_categories,related_search_volume,related_search_terms,up_month,review_types

import pandas as pd
import utils
import trend as trend
def update_search_volumes(trend_analysis_df, related_keywords_table, category_dict, search_volume_dict, search_keyword, analysis_info, info_dict):
    if trend_analysis_df is None or '연관검색어' not in trend_analysis_df.columns or trend_analysis_df['연관검색어'].empty:
        return

    # 업데이트: 키워드 카테고리와 관련 검색어 볼륨
    first_related_keyword = trend_analysis_df['연관검색어'].iloc[0]
    if search_keyword in category_dict:
        category_dict[search_keyword].append(first_related_keyword)
    else:
        category_dict[search_keyword] = [first_related_keyword]

    if '연관키워드' not in related_keywords_table.columns:
        print("'연관키워드' 컬럼이 related_keywords_table에 존재하지 않습니다.")
        return

    # 연관키워드에 대한 월간검색수_합계 가져오기 및 info_dict 업데이트
    related_row = related_keywords_table[related_keywords_table['연관키워드'] == first_related_keyword]
    if not related_row.empty:
        search_volume_dict[first_related_keyword] = related_row['월간검색수_합계'].values[0]
        # 여기에서 '연관검색어의 첫 번째 값에 대한 추가 정보'를 업데이트합니다.
        info_dict[first_related_keyword] = analysis_info
    else:
        print(f"'{first_related_keyword}'에 대한 월간검색수_합계 정보가 없습니다.")





def check_result(**kwargs):

    # 추출: 결과 데이터프레임과 그래프 데이터프레임, 분석 정보, 관련 검색어 정보
    trend_analysis_df = kwargs.get('tmp')
    graph_data_df = kwargs.get('tmp_gph')
    analysis_info = kwargs.get('tmp_info')
    trend_df = kwargs.get('trend_df')
    graph_df = kwargs.get('graph_df')
    search_keyword = kwargs.get('keywordName')
    category_dict = kwargs.get('keyword_categories')
    search_volume_dict = kwargs.get('related_search_volume')
    related_keywords_table = kwargs.get('df_table')
    info_dict = kwargs.get('info_dict')
    related_search_terms = kwargs.get('related_search_terms')
    
        #검색어와 연관 검색어의 검색 볼륨을 업데이트합니다.
    update_search_volumes(trend_analysis_df, related_keywords_table, category_dict, search_volume_dict, search_keyword, analysis_info, info_dict)



    related_search_terms[search_keyword] = related_keywords_table['연관키워드'][:10].to_list()

            # 데이터프레임 업데이트
    trend_df = pd.concat([trend_df, trend_analysis_df], axis=1)
    graph_df = pd.concat([graph_df, graph_data_df], axis=0)

    return category_dict, search_volume_dict, info_dict, related_search_terms, trend_df, graph_df


def handle_api_call(keywordName, currentRequestCount, 
                            df_table, clients, apiCallCount, 
                            current_client_index, request_limit, api_url):
    
    '''
    
    '''
    if apiCallCount <= request_limit:
        # 현재 클라이언트 정보 가져오기
        client_id, client_secret, client_index = utils.get_client_info(clients, current_client_index)
        real_client_id = clients[client_id]['client_id']

        # 로깅
        utils.log_progress(keywordName, currentRequestCount, len(df_table), client_id, apiCallCount, request_limit)
        
        # 관련 키워드 추출
        related_keyword = df_table['연관키워드'][currentRequestCount]

        # API 요청 데이터 준비
        request_data = {
            'keywordName': keywordName,
            'search_keyword': related_keyword,
            'client_id': real_client_id,
            'client_secret': client_secret,
            'api_url': api_url
        }

        # API 요청 데이터를 DataFrame에 추가
        return request_data, apiCallCount + 1, current_client_index
    else:
        # 요청 한도 초과 시 클라이언트 인덱스 업데이트
        current_client_index += 1
        if current_client_index >= len(clients):
            print("모든 API 클라이언트의 요청 한도 초과")
            return None, apiCallCount, current_client_index  # 처리 중단을 위한 None 반환
        else:
            # 클라이언트 전환 후 재시도
            return handle_api_call(keywordName, currentRequestCount, df_table, clients, 1, current_client_index, request_limit, api_url)



# 데이터 규격화 함수
def map_columns_based_on_keys(review_types, mode):
    # 'mode' 키와 'trend_df'가 존재하며, 해당 'trend_df' 값이 None이 아닌지 확인
    if mode in review_types and review_types[mode].get('trend_df') is not None:
        trend_df = review_types[mode]['trend_df']
        
        # 필요한 컬럼이 trend_df에 존재하는지 확인
        required_columns = ['검색일자', '연관검색어', '검색량']
        if not all(column in trend_df.columns for column in required_columns):
            # 필요한 컬럼이 없는 경우 예외 처리
            print(f"One or more required columns {required_columns} are missing in the DataFrame.")
            return None
        
        # 필요한 컬럼만 선택하여 새로운 DataFrame 생성
        final_df = trend_df[required_columns].copy()
        a = final_df.iloc[:, 0].tolist()
        final_dff = final_df[['검색량']].copy()
        final_dff.insert(0, '검색일자', a)
        keys_list = list(review_types[mode]['info_dict'].keys())
        
        # '검색일자' 컬럼을 포함하고, 나머지 컬럼에 keys_list의 키들을 매핑하기 위한 새 컬럼 이름 리스트 생성
        new_column_names = ['검색일자'] + keys_list
        final_dff.columns = new_column_names
        return final_dff
    else:
        # trend_df가 None인 경우 또는 mode 키가 존재하지 않는 경우 예외 처리
        print(f"The 'trend_df' for mode '{mode}' is None or the mode does not exist.")
        return None
    


def analyze_trend_data(api_request_data,keywordName,standard_time,review_types,up_month,day,df_table,keyword_categories,\
                       related_search_volume,related_search_terms):    
    unique_api_request_data  = api_request_data.drop_duplicates(subset=['search_keyword'])
    print(f'유일한 API 요청 데이터 수: {len(unique_api_request_data)}')

    for index, row in unique_api_request_data.iterrows():
        if row['keywordName'] != keywordName:
            continue

            
        trend_data = trend.trend_load(standard_time, row['search_keyword'], row['client_id'], row['client_secret'], row['api_url'])

        for review_key, settings in review_types.items():
                # 'monthly_rule' 유형의 처리를 먼저 확인
            if review_key == 'monthly_rule':
                tmp, tmp_gph, tmp_info, rising_month = settings['function'](trend_data, day, settings['time_period'])
                    # row[search_keyword] : 해당 키워드의 연관키워드 리스트
                if tmp is not None:
                    if str(keywordName) not in up_month:
                        up_month[str(keywordName)] = rising_month
                continue
                
                # 나머지 유형의 일반적인 처리
            tmp, tmp_gph, tmp_info = settings['function'](trend_data, day, settings['time_period'])

            if tmp is None:
                continue

                # 결과 처리 로직에 사용될 인자들을 하나의 딕셔너리로 묶기
            check_result_args = {
                'tmp': tmp,
                'tmp_gph': tmp_gph,
                'tmp_info': tmp_info,
                'trend_df': settings['trend_df'],
                'graph_df': settings['graph_df'],
                'keywordName': keywordName,
                'keyword_categories': keyword_categories,
                'related_search_volume': related_search_volume,
                'df_table': df_table,
                'info_dict': settings['info_dict'],
                'related_search_terms': related_search_terms,
                    # 'currentKeywordData',: row['search_keyword']
            }
    
                # **kwargs를 사용하여 딕셔너리를 함수에 전달
            keyword_categories, related_search_volume, settings['info_dict'], related_search_terms, settings['trend_df'], settings['graph_df'] = check_result(**check_result_args)
    return keyword_categories,related_search_volume,related_search_terms,up_month,review_types



def collect_and_analyze_keyword_trends(keywords,state,day,total_keywords,\
                                       clients,request_limit,api_url,standard_time,review_types,up_month,apiCallCount,current_client_index,i,api_request_data,\
                                        keyword_categories,related_search_volume,related_search_terms):
    

    for keywordName   in keywords[state['keyword_index']:]:
            df_table = pd.read_csv('./data/rl_srch/' + str(day) + f'/{keywordName}.csv', encoding='euc-kr')
            print(f'################################################ {keywordName } ({i+1}/{total_keywords}) ################################################')
            maxKeyword = min(50, len(df_table))   # 최대 연관검색어 수 (50개가 안되면 DF_TABLE의 길이만큼)

            for currentRequestCount  in range(state['currentRequestCount_index'], maxKeyword):
                # 설명

                request_data, apiCallCount, current_client_index = handle_api_call(
                    keywordName, currentRequestCount, df_table, clients, apiCallCount, 
                    current_client_index, request_limit, api_url)

                if request_data is not None:
                    # 데이터 프레임에 API 요청 데이터 추가
                    new_row = pd.DataFrame([request_data])
                    api_request_data = pd.concat([api_request_data, new_row], ignore_index=True)
                else:
                    # API 요청 한도 초과 시 처리
                    break

            if current_client_index >= len(clients):
                print("모든 API 클라이언트의 요청 한도 초과")
                break

            i += 1 
            print(f'API 요청 데이터 수: {len(api_request_data)}')


            keyword_categories,related_search_volume,related_search_terms,up_month,review_types\
                =analyze_trend_data(api_request_data,keywordName,standard_time,review_types,up_month,day,df_table,keyword_categories,\
                       related_search_volume,related_search_terms)
            

    return keyword_categories,related_search_volume,related_search_terms,up_month,review_types



