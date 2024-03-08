import asyncio
import time
from pytrends.request import TrendReq
from concurrent.futures import ThreadPoolExecutor

# 비동기 작업을 위한 Executor 인스턴스를 생성합니다.
executor = ThreadPoolExecutor(max_workers=5)

async def fetch_rising_queries(word: str, max_retries: int = 3) -> dict:
    pytrends = TrendReq(hl='ko-KR', tz=540, retries=2)
    kw_list = [word]

    for attempt in range(max_retries):
        try:
            loop = asyncio.get_running_loop()
            # 비동기로 실행하기 위해 run_in_executor를 사용합니다.
            await loop.run_in_executor(executor, lambda: pytrends.build_payload(kw_list, timeframe='today 1-m', geo='KR', gprop=''))
            result = await loop.run_in_executor(executor, pytrends.related_queries)
            rising_queries = result[word]['rising']
            if rising_queries is not None:
                return {word: list(rising_queries['query'])}
            return {word: []}
        except Exception as e:
            print(f"Error fetching data for {word}: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return {word: []}  # Return empty dict after max_retries

async def collect_rising_keywords(keywords: list) -> dict:
    tasks = [fetch_rising_queries(word) for word in keywords]
    results = await asyncio.gather(*tasks)
    keyword_results = {}
    for result in results:
        keyword_results.update(result)
    return keyword_results

if __name__ == "__main__":
    keywords = ["비트코인", "업비트"]  # 분석하고 싶은 키워드 목록
    
    # 비동기 함수 실행
    results = asyncio.run(collect_rising_keywords(keywords))
    
    print(results)
