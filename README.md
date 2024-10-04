# FinTrendX

## 프로젝트 소개
FinTrendX는 사람들이 금융 관련 키워드를 네이버에 검색하면서 얻은 데이터를 통해, 현재 어떤 키워드가 핫한지, 어떤 키워드가 지속적으로 상승하고 있는지를 확인하기 위한 프로젝트입니다. 연관 검색어, 트렌드 데이터, 뉴스, 블로그 데이터를 수집하고 분석하여 급상승, 지속상승, 규칙성을 보이는 데이터를 분류하는 것을 목표로 합니다.


## 프로젝트 구조
1. 메인 키워드별 연관검색어 집계
2. 각 키워드별 트렌드데이터 집계
3. 선별함수를 통한 급상승/지속상승/규칙성 데이터 분류
4. 네이버 뉴스데이터/구글검색어 데이터 집계 (비고: 구글검색어 데이터는 api 자체 오류 다분)
5. 블로그데이터를 통한 활동성 데이터 집계
6. 전체 데이터 Merge

## 작업 흐름
1. 사용자가 지정한 대분류 키워드를 입력합니다.
2. 네이버 API를 통해 해당 키워드들의 연관검색어를 추출합니다.
3. 네이버 트렌드 API를 사용하여 추출한 연관검색어들의 검색어 추이 데이터를 수집합니다.
4. 선별 함수를 통해 일별/주별/월별 데이터를 분석하여 급상승, 지속상승, 규칙성을 보이는 키워드를 추출합니다.
5. 추출된 키워드들을 바탕으로 네이버 뉴스데이터와 구글 검색어 API를 사용하여 데이터를 가져옵니다.
   _(비고: 구글 검색어 API는 오류가 발생할 수 있음)_
6. 모든 데이터를 종합하여 하나의 데이터셋으로 Merge합니다.

## 데이터 선별함수에서 고려된 점

<img src="https://github.com/user-attachments/assets/777e5be8-51d5-403b-bca2-2d6426fc1ea2" alt="트렌드 분석 " width="600"/>



## 결과물
- 결과 페이지: [https://trendkey-7a41071967af.herokuapp.com/](https://trendkey-7a41071967af.herokuapp.com/)

<img src="https://github.com/user-attachments/assets/0a838bd9-6a99-4dde-b44f-eb589069535b" alt="트렌드 분석 결과 차트" width="600"/>

**[그림 1]** 트렌드 분석 결과 시각화
## 주의사항
반드시 09시 이후에 실행할 것 (API 업데이트가 9시 정각에 이루어짐)
