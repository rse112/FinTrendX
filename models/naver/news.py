import asyncio
import aiohttp
import sys
import os
# 현재 스크립트의 경로를 기준으로 상위 디렉토리의 절대 경로를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import utils
def clean_text(text):
    """
    HTML 태그 제거 및 특수 문자 처리 함수
    """
    text = text.replace('<b>', ' ').replace('</b>', ' ')
    text = text.replace('&quot;', '"').replace('&apos;', '\'')
    text = text.replace('amp;', '').replace('&lt;', '<').replace('&gt;', '>')
    return text

async def fetch_news(session, search_term, headers, params, attempts=10):
    """
    네이버 API를 통해 뉴스 데이터를 비동기적으로 가져오는 함수
    """
    backoff = 1
    for attempt in range(attempts):
        try:
            async with session.get("https://openapi.naver.com/v1/search/news.json", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['items']
                else:
                    raise Exception(f"Error fetching data for {search_term}: {response.status}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < attempts - 1:
                await asyncio.sleep(3 * backoff)
                backoff *= 2
            else:
                raise

async def news_result_async(names):
    """
    검색어별 뉴스 제목, 본문, 링크 추출 및 필터링하는 비동기 함수
    """
    client_id = utils.get_secret("Naver_blog_id")
    client_secret = utils.get_secret("Naver_blog_pw")
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_news(session, name, headers, {"query": name, "display": 100, "sort": "date"}) for name in names]
        results = await asyncio.gather(*tasks)
        
        results_dict = {}
        for name, result in zip(names, results):
            titles_links = [(clean_text(item['title']), item['link']) for item in result[:10] if result]
            results_dict[name] = titles_links
            
    return results_dict

async def main(keywords):
    """
    비동기 실행을 위한 메인 함수, 키워드 리스트를 분할하여 처리
    """
    return await news_result_async(keywords)

if __name__ == "__main__":
    target_keywords = ["테스트", "예제"]  # 테스트 키워드
    news_data = asyncio.run(main(target_keywords))
    print(news_data)
