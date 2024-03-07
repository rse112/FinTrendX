from difflib import SequenceMatcher

# HTML 태그 제거 및 특수 문자 처리 함수
def clean_text(text):
    text = text.replace('<b>', ' ').replace('</b>', ' ')
    text = text.replace('&quot;', '"').replace('&apos;', '\'')
    text = text.replace('amp;', '').replace('&lt;', '<').replace('&gt;', '>')
    return text

# 검색어별 뉴스 제목, 본문, 링크 추출 및 필터링 함수
def news_result(names):
    titles, descs, links, index_list = [], [], [], []
    existing_titles = set()  # 기존 제목 관리용

    for name in names:
        json_data = news(name)
        if not json_data:  # 뉴스 데이터가 없는 경우 스킵
            continue

        tmp_titles, tmp_links = [], []
        count = min(len(json_data), 10)  # 최대 10개 항목 처리

        for i, item in enumerate(json_data):
            if i >= count:
                break

            # 뉴스 제목 필터링 및 처리
            title = clean_text(item['title'])
            if any(keyword in title for keyword in ['운세', '칼럼', '인사']) or title in existing_titles:
                continue  # 필터링 조건에 맞는 경우 스킵

            # 유사 제목 체크
            if any(SequenceMatcher(None, title, existing).ratio() > 0.8 for existing in existing_titles):
                continue

            # 제목, 본문, 링크 추가
            tmp_titles.append(title)
            existing_titles.add(title)  # 처리된 제목 추가
            descs.append(clean_text(item['description']))
            tmp_links.append(item['link'])
            index_list.append(len(tmp_titles))  # 인덱스 추가

        titles.append(tmp_titles)
        links.append(tmp_links)

    return titles, descs, links, index_list


import requests

def news(search_term, display=100):
    client_id = "ByXmMvAqMIxyVUY_h17L"
    client_secret = "2x7yByvNSN"
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": search_term,
        "display": display,
        "sort": "date"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['items']
    else:
        print(f"Error fetching data for {search_term}: {response.status_code}")
        return []

# 예시 사용 방법
names = ["Python", "AI"]
results = news_result(names)
for result in results:
    print(result)