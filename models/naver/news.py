import aiohttp
import asyncio
import json
from datetime import datetime
import os

client_id = "ByXmMvAqMIxyVUY_h17L"
client_secret = "2x7yByvNSN"

# 비동기 API 요청 함수
async def getRequestUrl(url, session):
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Error: API response status {response.status}")
                return None
    except Exception as e:
        print(f"Exception occurred while making API request: {e}")
        return None

# 네이버 검색 API 비동기 호출 함수
async def getNaverSearch(node, srcText, start, display, session):
    base = "https://openapi.naver.com/v1/search"
    node = f"/{node}.json"
    parameters = f"?query={srcText}&start={start}&display={display}"
    url = base + node + parameters
    responseDecode = await getRequestUrl(url, session)

    if responseDecode is None:
        return None
    else:
        return json.loads(responseDecode)

# 비동기식 뉴스 수집 함수
async def news(name, display=100):
    async with aiohttp.ClientSession() as session:
        jsonResult = await getNaverSearch('news', name, 1, display, session)
        if jsonResult is None:
            print(f"Failed to fetch data for {name}")
            return None
        return jsonResult  # Return the result for further processing

# 파일 저장 함수 (동기적으로 처리)
def saveResults(srcText, node, jsonResult):
    baseDir = "./data/json"
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)
    fileName = f"{srcText}_naver_{node}.json"
    filePath = os.path.join(baseDir, fileName)
    with open(filePath, 'w', encoding='utf8') as outfile:
        jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(jsonFile)

# 파일 존재 여부를 확인하는 함수
def checkFileExists(srcText, node):
    baseDir = "./data/json"
    fileName = f"{srcText}_naver_{node}.json"
    filePath = os.path.join(baseDir, fileName)
    return os.path.exists(filePath)

# 비동기식 메인 실행 함수
async def main():
    queries = ["Python", "AsyncIO", "Aiohttp","디도스","클라우드 보안","사이버 공격","주식","비트코인","테슬라","삼성전자","네이버","퇴직연금"]
    for query in queries:
        if not checkFileExists(query, 'news'):
            jsonResult = await news(query)
            if jsonResult:
                saveResults(query, 'news', jsonResult)
                print(f"{query}에 대한 뉴스 수집이 완료되었습니다.")
            else:
                print(f"No results for {query} or an error occurred.")

if __name__ == '__main__':
    asyncio.run(main())
