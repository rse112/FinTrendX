import time
import requests
import os
import hmac
import hashlib
import base64
from utils import get_secret

# import aiohttp
# import asyncio
# class APIClient:
#     def __init__(self, base_url, customer_id, api_key, secret_key,uri, method):
#         self.base_url = base_url
#         self.customer_id = customer_id
#         self.api_key = api_key
#         self.secret_key = secret_key
#         self.uri = uri
#         self.method = method

#     def generate(self, timestamp, method, method_uri):
#         message = f"{timestamp}.{method}.{method_uri}"
#         hash = hmac.new(bytes(self.secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
#         hash.hexdigest()
#         return base64.b64encode(hash.digest()).decode("utf-8")
        
#     def get_header(self, method, uri):
#         timestamp = str(round(time.time() * 1000))
#         signature = self.generate(timestamp, method, uri)
#         return {
#             'Content-Type': 'application/json; charset=UTF-8',
#             'X-Timestamp': timestamp,
#             'X-API-KEY': self.api_key,
#             'X-Customer': str(self.customer_id),
#             'X-Signature': signature
#         } 
    
#     def get_data(self, query):
#         """API로부터 데이터를 가져오는 함수"""
        
#         header = self.get_header(method=self.method, uri=self.uri)
#         url = self.base_url + self.uri
#         response = requests.get(url, headers=header, params=query)
#         return response

#     @staticmethod
#     def make_directory(path):
#         os.makedirs(path, exist_ok=True)


# if __name__ == "__main__":
#     start = time.time()
    
#     # API 설정

#     BASE_URL = get_secret("BASE_URL")
#     CUSTOMER_ID = get_secret("CUSTOMER_ID")
#     API_KEY = get_secret("API_KEY")
#     SECRET_KEY = get_secret("SECRET_KEY")
#     URI = get_secret("URI")
#     METHOD = get_secret("METHOD")
#     # API 클라이언트 인스턴스 생성
#     api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY,URI,METHOD)
#     # API 요청을 위한 쿼리 파라미터 정의
#     query = {'siteld':'', 'bixtpld':'', 'event' : '','month': '', 'showDetail':'1',
#                 'hintKeywords': '주식'}

#     # API로부터 데이터 가져오기
#     response = api_client.get_data( query)

#     # 응답 출력
#     if response.status_code == 200:
#         # 성공적으로 데이터를 받아온 경우
#         print("API 호출 성공:")
#         print(response.json())  # JSON 응답을 직접 출력
#         print(time.time()-start) 
#     else:
#         # API 호출 실패
#         print("API 호출 실패, 상태 코드:", response.status_code)

#
import aiohttp
import asyncio
import os
import hmac
import hashlib
import base64
import time

class APIClient:
    def __init__(self, base_url, customer_id, api_key, secret_key, uri, method):
        self.base_url = base_url
        self.customer_id = customer_id
        self.api_key = api_key
        self.secret_key = secret_key
        self.uri = uri
        self.method = method

    def generate(self, timestamp, method, method_uri):
        message = f"{timestamp}.{method}.{method_uri}"
        hash = hmac.new(bytes(self.secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
        hash.hexdigest()
        return base64.b64encode(hash.digest()).decode("utf-8")

    async def get_header(self, method, uri):
        timestamp = str(round(time.time() * 1000))
        signature = self.generate(timestamp, method, uri)
        return {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Timestamp': timestamp,
            'X-API-KEY': self.api_key,
            'X-Customer': str(self.customer_id),
            'X-Signature': signature
        }

    async def get_data(self, query):
        headers = await self.get_header(method=self.method, uri=self.uri)
        url = self.base_url + self.uri
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=query) as response:
                return await response.json()

    @staticmethod
    def make_directory(path):
        os.makedirs(path, exist_ok=True)
from utils import get_secret

async def main():
    # 이 부분은 실제 환경에 맞게 조정 (환경 변수 또는 구성 파일 사용 권장)
    BASE_URL = get_secret("BASE_URL")
    CUSTOMER_ID = get_secret("CUSTOMER_ID")
    API_KEY = get_secret("API_KEY")
    SECRET_KEY = get_secret("SECRET_KEY")
    URI = get_secret("URI")
    METHOD = get_secret("METHOD")
    # API 클라이언트 인스턴스 생성
    api_client = APIClient(BASE_URL, CUSTOMER_ID, API_KEY, SECRET_KEY,URI,METHOD)
    # API 요청을 위한 쿼리 파라미터 정의
    query = {'siteld':'', 'bixtpld':'', 'event' : '','month': '', 'showDetail':'1',
                'hintKeywords': '주식'}

    start = time.time()
    response = await api_client.get_data(query)
    
    print("API 호출 결과:")
    print(response)
    print(f"소요 시간: {time.time() - start} 초")


if __name__ == "__main__":
    asyncio.run(main())



###

