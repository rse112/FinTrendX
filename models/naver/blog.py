import sys
import os
# 현재 스크립트의 경로를 기준으로 상위 디렉토리의 절대 경로를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import asyncio
import aiohttp
import json
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import utils
sem = asyncio.Semaphore(10)  # 동시 요청 수를 10으로 제한
async def fetch_blog(session, url, headers, retries=3):
    async with sem:  # 세마포어를 사용하여 동시 요청 수 제한
        try:
            async with session.get(url, headers=headers) as response:
                rescode = response.status
                if rescode == 200:
                    response_body = await response.text()
                    response_json = json.loads(response_body)
                    
                    return pd.DataFrame(response_json['items'])
                else:
                    
                    return pd.DataFrame()
        except Exception as e:
            print(f"Request failed, {retries} retries left. Error: {e} for URL: {url}")
            if retries > 0:
                await asyncio.sleep(1)  # 잠시 대기 후 재시도
                return await fetch_blog(session, url, headers, retries-1)
            else:
                print(f"All retries failed for URL: {url}")
                return pd.DataFrame()


async def blog_async(client_id, client_secret, query, display, start, sort):
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display={str(display)}&start={str(start)}&sort={sort}"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    async with aiohttp.ClientSession() as session:
        return await fetch_blog(session, url, headers)

async def blog_result_async(types, std_time, client_id, client_secret):
    end_time = std_time - relativedelta(days=1)
    start_time = std_time - relativedelta(weeks=1) - relativedelta(days=1)
    end_time = end_time.strftime("%Y-%m-%d")
    start_time = start_time.strftime("%Y-%m-%d")

    display = 100
    sort = 'date'

    tasks = []
    for type_ in types:
        query = f'{type_}'
        for i in range(10):  # 10번 반복하여 총 1000개의 블로그 포스트 수집
            start = 1 + 100 * i
            tasks.append(blog_async(client_id, client_secret, query, display, start, sort))

    results = await asyncio.gather(*tasks)
    
    # 결과 데이터프레임을 합치고 활동성 지표를 계산
    all_results = pd.DataFrame()
    for result in results:
        all_results = pd.concat([all_results, result], ignore_index=True)
        
    # 'postdate' 열을 datetime 객체로 변환
    all_results['postdate'] = pd.to_datetime(all_results['postdate'], format='%Y%m%d')
    
    blog_active = []
    for type_ in types:
        filtered_results = all_results[all_results['title'].str.contains(type_)]
        recent_posts_count = filtered_results[
            (filtered_results['postdate'] >= pd.to_datetime(start_time)) & 
            (filtered_results['postdate'] <= pd.to_datetime(end_time))
        ].shape[0]
        
        # 활동성 지표 계산: 최근 일주일 동안 블로그 발간 비율
        activity_rate = round((recent_posts_count / 1000) * 100, 3)
        blog_active.append((type_, activity_rate))
    
    return blog_active
def load_list_from_text(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]



if __name__ == "__main__":

    target_keywords = load_list_from_text('./data/target_keywords/240313/target_keywords.txt')
    # 테스트를 위한 변수 정의
    client_id = utils.get_secret("Naver_blog_id")
    client_secret = utils.get_secret("Naver_blog_pw")
    # types = ["신용카드발급", "파이썬"]  # 검색하고자 하는 키워드 목록
    std_time = datetime.now()  # 기준 시간 설정
    # target_keywords=['파이썬','망고']
    # 비동기 메인 함수 실행
    results = asyncio.run(blog_result_async(target_keywords, std_time, client_id, client_secret))
    df_results = pd.DataFrame(results, columns=['Keyword', 'Activity Rate'])
    df_results.to_csv('keyword_activity_rates.csv', index=False)
    # 결과 출력 (테스트 목적)
    print(results)
