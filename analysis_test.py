import asyncio
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import utils
from trend import trend_maincode
import time
from pytz import timezone
import select_keyword
import asyncio
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import utils
from trend import trend_maincode
import time
from pytz import timezone
import select_keyword

class analysis:
    def __init__(self):
        # 기본설정
        self.formatted_today, self.day=utils.get_today_date()
        self.state=utils.load_state()
        self.apiCallCount = self.state.get('api_request_count', 1)
        self.current_client_index = self.state.get('current_client_index', 0)
        self.keywords = utils.load_keywords('main_keyword.json')['keyword_final']
        self.request_limit = 1000
        self.keyword_index = self.state['keyword_index']
        self.standard_time = datetime.now()
        self.api_url = "https://openapi.naver.com/v1/datalab/search"
        self.today = datetime.now(timezone('Asia/Seoul'))
        self.api_request_data = pd.DataFrame(columns=['search_keywords'])
        self.start_index = (self.today - relativedelta(days=1)).strftime("%Y-%m-%d")
        self.end_index = (self.today - relativedelta(years=3) - relativedelta(days=1)).strftime("%Y-%m-%d")
        self.clients = utils.get_secret("clients")
        

        self.api_request_data_dataname = {
                'api_request_data': [],
                'keyname': []
        }

        # 데이터프레임 초기화
        self.trends_dataframes = {
        'daily_up': pd.DataFrame(),
        'weekly_up': pd.DataFrame(),
        'weekly_stay': pd.DataFrame(),
        'monthly_up': pd.DataFrame(),
        'monthly_stay': pd.DataFrame(),
        'monthly_rule': pd.DataFrame()
        }


        self.graph_tables = {
        'day': pd.DataFrame(index=pd.date_range(start=self.start_index, end=self.end_index, freq='1d')),
        'week': pd.DataFrame(index=pd.date_range(start=self.start_index, end=self.end_index, freq='7d')),
        'month': pd.DataFrame(index=pd.date_range(start=self.start_index, end=self.end_index, freq='28d'))
        }

        # 정보 저장을 위한 딕셔너리 초기화
        self.keyword_data = {
            'keyword_categories': {},
            'related_search_terms': {},
            'related_search_volume': {},
            'up_month': {}
        }
        self.review_types = {
                'daily': {
                        'function': select_keyword.select_keyword,
                        'info_dict': {},
                        'trend_df': self.trends_dataframes['daily_up'],
                        'graph_df': self.graph_tables['day'],
                        'time_period': 'daily'
                    },
            'weekly_up': {
                        'function': select_keyword.select_keyword,
                        'info_dict': {},
                        'trend_df': self.trends_dataframes['weekly_up'],
                        'graph_df': self.graph_tables['week'],
                        'time_period': 'weekly'
                    },
            'weekly_stay': {
                        'function': select_keyword.rising_keyword_analysis,
                        'info_dict': {},
                        'trend_df': self.trends_dataframes['weekly_stay'],
                        'graph_df': self.graph_tables['month'],
                        'time_period': 'weekly'
                    },
            'monthly_up': {
                        'function': select_keyword.select_keyword,
                        'info_dict': {},
                        'trend_df': self.trends_dataframes['monthly_up'],
                        'graph_df': self.graph_tables['month'],
                        'time_period': 'month'
                    },
            'monthly_stay': {
                        'function': select_keyword.rising_keyword_analysis,
                        'info_dict': {},
                        'trend_df': self.trends_dataframes['monthly_stay'],
                        'graph_df': self.graph_tables['month'],
                        'time_period': 'month'
                    },
            'monthly_rule': {
                        'function': select_keyword.monthly_rule,
                        'info_dict': {},
                        'trend_df': self.trends_dataframes['monthly_rule'],
                        'graph_df': self.graph_tables['month'],
                        'time_period': 'month'
                    }
                }
        pass


        # api 설정
    def handle_api_call(self,keywordName,df_table,currentRequestCount):
        if self.apiCallCount<= self.request_limit:
            id_num,pw,_=utils.get_client_info(self.clients,self.current_client_index)
            id = self.clients[id_num]['client_id']
            pw=self.clients[id_num]['client_secret']
            utils.log_progress(keywordName, currentRequestCount, \
                               len(df_table), id, self.apiCallCount, self.request_limit)
            related_keyword = df_table['연관키워드'][currentRequestCount]
            request_data = {
            
            'search_keywords': related_keyword,

            }        
            return request_data, self.apiCallCount + 1, self.current_client_index
        else:
                # 요청 한도 초과 시 클라이언트 인덱스 업데이트
                self.current_client_index += 1
                if self.current_client_index >= len(self.clients):
                    print("모든 API 클라이언트의 요청 한도 초과")
                    return None, self.apiCallCount, self.current_client_index  # 처리 중단을 위한 None 반환
                else:
                    # 클라이언트 전환 후 재시도
                    return self.handle_api_call(keywordName, currentRequestCount, df_table)
                
    # 연관 검색어의 trend 데이터
    def analyze_trend_data(self, uniq):
        params = {
            "search_keywords": uniq["api_request_data"],  
            "id": self.clients['id_1']["client_id"],
            "pw": self.clients['id_1']["client_secret"],
            "api_url": self.api_url
        }
        trend_data = asyncio.run(trend_maincode(params,self.clients, self.api_url))
        return trend_data
    
    # 연관검색어의 급상승, 지속상승 로직 적용
    def select_keywords(self, trend_data):
        review_settings = {key: [] for key in self.review_types.keys()}
        for i, (index, row) in enumerate(trend_data.iterrows()):
            # 각 행의 첫 번째 열과 두 번째 열의 값 참조
            first_column_value = row['trend_data']
            second_column_value = row['keyname']
            
            for review_key, settings in self.review_types.items():
                if review_key == 'monthly_rule':
                    # monthly_rule에 대한 특별 처리
                    trend_analysis_df, graph_data_df, analysis_info, rising_month = settings['function'](first_column_value, self.day, settings['time_period'])
                    if trend_analysis_df is not None:
                        review_settings[review_key].append((trend_analysis_df, graph_data_df, analysis_info, rising_month, second_column_value,first_column_value.columns[0]))
                else:
                    # 기타 경우 처리
                    trend_analysis_df, graph_data_df, analysis_info = settings['function'](first_column_value, self.day, settings['time_period'])
                    if trend_analysis_df is not None:
                        review_settings[review_key].append((trend_analysis_df, graph_data_df, analysis_info, second_column_value,first_column_value.columns[0]))
        return review_settings
                            # tmp 랑 tmp_gph, tmp_info 얘네를 딕셔너리에 집어넣는 함수

    #     #딕셔너리에 데이터를 넣는 함수
    def insert_data_into_dict(self):
        
        pass



    def collect_and_analyze_keyword_trends(self,keyword_grouped_dfs):
        total_keywords = len(self.keywords)
        api_request_data_list = []  # DataFrame 대신 사용할 리스트
        
        for keywordIndex, keywordName in enumerate(self.keywords[self.keyword_index:], start=self.keyword_index):
            
            df_table = pd.read_csv(f'./data/rl_srch/{self.day}/{keywordName}.csv', encoding='euc-kr')
            print(f'################################################ {keywordName} ({keywordIndex+1}/{total_keywords}) ################################################')
            maxKeyword = min(50, len(df_table))

            for currentRequestCount in range(self.state['currentRequestCount_index'], maxKeyword):
                request_data, self.apiCallCount, self.current_client_index = self.handle_api_call(keywordName, df_table, currentRequestCount)
                self.api_request_data_dataname['keyname'].append(keywordName)
                # API 요청 예외 처리 (한도 초과 시 클라이언트 인덱스 업데이트)
                if request_data is not None:
                    api_request_data_list.append(request_data)  # 리스트에 데이터 추가
                else:
                    break

            if self.current_client_index >= len(self.clients):
                print("모든 API 클라이언트의 요청 한도 초과")
                break

            self.keyword_index += 1

        # 리스트를 DataFrame으로 변환
            
        if api_request_data_list:
            self.api_request_data = pd.DataFrame(api_request_data_list)
            api_data_list = self.api_request_data['search_keywords'].tolist()

            self.api_request_data_dataname['api_request_data'] = api_data_list
        print(f'API 요청 데이터 수: {len(self.api_request_data)}')


        uniq=utils.merge_keys_for_unique_names(self.api_request_data_dataname)
        trend_data = pd.DataFrame({'trend_data': self.analyze_trend_data(uniq), 'keyname': uniq['keyname']})
        return trend_data
        # 실시간 급상승 이런거 들어가는 함수부분
  
if __name__ == "__main__":
    start=time.time()
    analysis_instance = analysis()
    trend_data=analysis_instance.collect_and_analyze_keyword_trends()
    analysis_instance.select_keywords(trend_data)
    print(time.time()-start)