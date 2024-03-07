import time
from pytrends.request import TrendReq

def fetch_rising_queries(word, max_retries=3):
    pytrends = TrendReq(hl='ko-KR', tz=540, retries=2)
    kw_list = [word]

    for attempt in range(max_retries):
        try:
            pytrends.build_payload(kw_list, geo='KR', timeframe='today 1-m', cat=0, gprop='')
            result = pytrends.related_queries()
            rising_queries = result[word]['rising']
            if rising_queries is not None:
                return list(rising_queries['query'])
            return []
        except Exception as e:
            print(f"Error fetching data for {word}: {e}")
            time.sleep(2 ** attempt) # Exponential backoff
    return [] # Return empty list after max_retries

def collect_rising_keywords(keywords):
    results = []
    for word in keywords:
        rising_keywords = fetch_rising_queries(word)
        results.append(rising_keywords)
    return results


if __name__ == "__main__":
    keywords = ["비트코인", "업비트"]  # 분석하고 싶은 키워드 목록
    results = collect_rising_keywords(keywords)
    print(results)
