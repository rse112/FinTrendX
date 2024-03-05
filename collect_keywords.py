import utils
import pandas as pd
import time
from utils import get_secret 
from api_set import APIClient
from datetime import datetime
from pytz import timezone
import os
from datetime import datetime
from pytz import timezone
import asyncio


async def collect_keywords(srch_keyword, day):
    # API 설정값은 실제 환경에 맞게 설정하세요.
    BASE_URL = get_secret("BASE_URL")
    CUSTOMER_ID = get_secret("CUSTOMER_ID")
    API_KEY = get_secret("API_KEY")
    SECRET_KEY = get_secret("SECRET_KEY")
    URI = get_secret("URI")
    METHOD = get_secret("METHOD")
    
    api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY, URI, METHOD)
    tmp_df = pd.DataFrame()
    main_keyword = utils.load_keywords('main_keyword.json')  # 경로는 실제 환경에 맞게 조정
    total_keywords = sum(len(main_keyword[word]) for word in srch_keyword)
    #################################
    i = 1
    g=globals()
    tasks=[]
    for word in srch_keyword:
        print(word)
        key_list = []
        print(f'{word} 연관검색어 추출 시작!!')
        for keyword in main_keyword[word]:
            
            query = {
                'siteld': '',
                'bixtpld': '',
                'event': '',
                'month': '',
                'showDetail': '1',
                'hintKeywords': keyword
            }
            #r_data = await api_client.get_data(query)
            task = asyncio.create_task(api_client.get_data(query))
            tasks.append(task)
            responses = await asyncio.gather(*tasks)

            for r_data in responses:
                if 'keywordList' in r_data:  # 'keywordList' 키가 응답 데이터에 있는지 확인
                

                    df_naver = pd.DataFrame(r_data['keywordList'])

                    # '< 10' 로 표기된 값들을 '9'로 변경
                    df_naver.replace('< 10', '9', inplace=True) 

                    # '< 10' 때문에 문자열로 인식된 컬럼 float으로 변경
                    columns_to_convert = ['monthlyPcQcCnt', 'monthlyMobileQcCnt']

                    # 각 열에 대해 데이터 타입 변환
                    for column in columns_to_convert:
                        df_naver[column] = df_naver[column].astype('float64')

                    # 월간'총'검색수 생성()
                    df_naver.insert(loc=3, column='monthlyTotalCnt', value=df_naver['monthlyPcQcCnt'] + df_naver['monthlyMobileQcCnt'])
                    # '월간총검색수'로 내림차순 정리
                    df_naver = df_naver.sort_values('monthlyTotalCnt', ascending=False).reset_index(drop=True)
                    # 컬럼명 한글로 변경
                    df_naver = df_naver.rename(columns={'relKeyword': '연관키워드',
                                                        'monthlyPcQcCnt': '월간검색수_PC',
                                                        'monthlyMobileQcCnt': '월간검색수_모바일',
                                                        'monthlyTotalCnt': '월간검색수_합계',
                                                        'monthlyAvePcClkCnt': '월평균클릭수_PC',
                                                        'monthlyAveMobileClkCnt': '월평균클릭수_모바일',
                                                        'monthlyAvePcCtr': '월평균클릭률_PC',
                                                        'monthlyAveMobileCtr': '월평균클릭률_모바일',
                                                        'plAvgDepth': '월평균노출광고수',
                                                        'compIdx': '경쟁정도'})

                    ## 테이블 저장 ##
                tmp_table = df_naver[['연관키워드', '월간검색수_합계']].copy()
                if len(tmp_table.index) >= 0:
                        g[f'df_{keyword}'] = tmp_table  # 검색어 연관검색어 정보 테이블
                        tmp_table.to_csv(f'./data/rl_srch/{day}/{keyword}.csv', encoding='euc-kr', index=False)  # csv 형태로 저장
                        key_list.append(keyword)
                        tmp = pd.DataFrame(tmp_table.head(25))
                        tmp_df = pd.concat([tmp_df, tmp])
                        
            # 연관검색어 수집 진행률 표시
            
                # 반복문 진행률 표시
            print(f'{int(i / total_keywords * 100)}% complete!')
            i += 1
                
    return tmp_df


async def main():
    today = datetime.now(timezone('Asia/Seoul'))
    day = today.strftime("%y%m%d")  # 예시 날짜
    srch_keyword = ["keyword_final"]  # 검색할 키워드 예시
    collected_data = await collect_keywords(srch_keyword, day)
    print(collected_data)


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)



    ### 동기적 프로그래밍(원래 함수) - > 비동기적 초감소 시간 : 



    ### 비동기 : 50.22434163093567
    ### 동기 : 
    