from concurrent.futures import ThreadPoolExecutor
import asyncio
from pytrends.request import TrendReq




executor = ThreadPoolExecutor(max_workers=5)



async def fetch_rising_queries(keyword: str, max_retries: int = 1) -> dict:


    pytrends = TrendReq(
        hl="ko-KR", tz=540, retries=1
    )
    kw_list = [keyword]

    for attempt in range(max_retries):
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                executor,
                lambda: pytrends.build_payload(
                    kw_list, timeframe="today 1-m", geo="KR", gprop=""
                ),
            )
            result = await loop.run_in_executor(executor, pytrends.related_queries)
            rising_queries = result[keyword]["rising"]
            if rising_queries is not None:
                return {keyword: list(rising_queries["query"])}
            return {keyword: []}
        except Exception as e:
            # print(
            #     f"Error fetching data for {keyword}: 시도횟수 : {attempt+1}/{max_retries},{e}"
            # )
            await asyncio.sleep(1**attempt)
    return {keyword: []}


async def collect_rising_keywords(target_keywords: list) -> dict:
    tasks = [fetch_rising_queries(keyword) for keyword in target_keywords]
    results = await asyncio.gather(*tasks)
    aggregated_results = {}
    for result in results:
        aggregated_results.update(result)
    return aggregated_results


if __name__ == "__main__":
    # 사용할 키워드 리스트 (예시)
    target_keywords = ["사과"]

    # 비동기 함수 실행하여 결과 수집
    rising_keywords_results = asyncio.run(collect_rising_keywords(target_keywords))
    print(rising_keywords_results)
