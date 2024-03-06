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
    BASE_URL = get_secret("BASE_URL")
    CUSTOMER_ID = get_secret("CUSTOMER_ID")
    API_KEY = get_secret("API_KEY")
    SECRET_KEY = get_secret("SECRET_KEY")
    URI = get_secret("URI")
    METHOD = get_secret("METHOD")
    api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY, URI, METHOD)
    main_keyword = utils.load_keywords('main_keyword.json') 

    tasks = []
    
    for word in srch_keyword:
        if word in main_keyword:
            for keyword in main_keyword[word]:
                query = {
                    'siteld': '',
                    'bixtpld': '',
                    'event': '',
                    'month': '',
                    'showDetail': '1',
                    'hintKeywords': keyword
                }
                task = asyncio.create_task(api_client.get_data(query))
                tasks.append(task)
    
    responses = await asyncio.gather(*tasks)

    all_keywords_data = pd.DataFrame()
    for response in responses:
        if 'keywordList' in response:
            df = pd.DataFrame(response['keywordList'])
            df.replace('< 10', '9', inplace=True)
            columns_to_convert = ['monthlyPcQcCnt', 'monthlyMobileQcCnt']
            for column in columns_to_convert:
                df[column] = df[column].astype('float64')
            df['monthlyTotalCnt'] = df['monthlyPcQcCnt'] + df['monthlyMobileQcCnt']
            df = df[['relKeyword', 'monthlyTotalCnt']]  # 관심 있는 컬럼만 선택
            df.rename(columns={'relKeyword': '연관키워드', 'monthlyTotalCnt': '월간검색수_합계'}, inplace=True)  # 컬럼명 변경
            all_keywords_data = pd.concat([all_keywords_data, df], ignore_index=True)

    return all_keywords_data



async def main():
    today = datetime.now(timezone('Asia/Seoul'))
    day = today.strftime("%y%m%d")
    srch_keyword = ["keyword_final"]
    collected_data = await collect_keywords(srch_keyword, day)
    print(collected_data)

if __name__ == "__main__":
    import time
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"Execution time: {end - start} seconds")