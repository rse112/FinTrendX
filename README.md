# (2024-03-13)

## 외부트렌드 분석

## 프로젝트 구조
--> 쓸모없는것들은 쳐내고
--> 원래 로직에서 어떻게 바뀌었는가를 중심적으로, 즉 현재 구조에서 원래 코드엔 어떻게 있었냐를 말하면 좋을듯

1. 메인키워드 선별

2. 메인키워드들의 연관검색어 분석(네이버 검색어트랜드 API 사용)
--> collect_keywords함수를 통해 연관검색어 탐색
--> 이 함수에서 연관검색어들의 월간검색어(검색량)을 검출
--> 월간검색어는 PC검색량+모바일검색량
--> 결과 : 컬럼 : 연관키워드,월간검색수_합계,검색어 인 데이터프레임 
--> 백업용으로 ./data/rl_srch에 저장
--> 예시 : 
연관키워드,월간검색수_합계,검색어
주식,562300.0,주식
미주부,410.0,주식
김현준대표,1030.0,주식
퀀트투자,6820.0,주식
--> 바뀐점 : 동기성프로그래밍적용, 모호한 변수명 변경



3. collect_keywords에서 구한 연관검색어들을 따로 모아 트랜드분석 진행(네이버 검색어트랜드 API 사용)
--> 사용된 메인함수 : trend_maincode
--> 분석기간 : 3년, 단위:하루
--> 현재 API제한으로 인해 500개씩 id를 배당해서 네이버트랜드API 작업
--> API제한 오류(Many request) 뜨면 다음 id로 넘어가서 작업하는 로직 추가(예정)
--> 결과물 : results(
    type: list
    result[0] : 첫번째 id에 배정된 연관검색어(500개) 각각의 트랜드데이터
    result[1] : 두번째 id에 ...
    result[2] : 세번째 id에 ..
    보통 result[2] 까지밖에 없음
)

--> 바뀐점 : 중복된 코드 통합, 동시성 프로그래밍 적용, 모호한 변수명 변경

4. trend_maincode에서 얻은 트랜드 데이터를 통해 병렬처리를 통한 키워드 분석집계
--> 사용된 메인함수 : execute_analysis
--> month_rule_list_a,rising_list_a,select_list_a에 각각 데이터 저장
--> month_rule_list_a : 월별규칙성 리스트
--> rising_list_a : 2개의 리스트를 가진 리스트로 각각
rising_list_a[0] : 주별 지속상승 키워드 리스트
rising_list_a[1] : 월별 지속상승 키워드 리스트
--> select_list_a에 : 급상승 리스트
select_list_a[0] : 일별 급상승 키워드 리스트
select_list_a[1] : 주별 급상승 키워드 리스트
select_list_a[2] : 월별 급상승 키워드 리스트

--> 바뀐점 : 병렬프로그래밍 적용, 모호한 변수명 변경


5. 구글트랜드 /네이버 검색어 및 뉴스데이터 크롤링
--> 주요함수 : collect_news_keywords(네이버 뉴스 데이터크롤링 함수 )
               collect_google_keywords(구글 트랜드 검색 함수)
--> 특이사항 : 비동기 프로그래밍을 통해 동시에 api를 받으면서 I/O작업 시간을 획기적으로 단축하였음
--> 데이터를 다 받앗으면 ./data/trend_data 폴더에 각각google_data , news_data로 저장

6. 활동성 데이터 수집
--> 주요함수 : main_blog_analysis
--> 바뀐점 : 동시성프로그래밍적용, 모호한 변수,함수명 변경

7. 받은 데이터 형식에 맞게 전처리
--> 바뀐점 : 하나하나 데이터를 불러오고 그런방식말고 전체의 df로 사용하면서 데이터의 효율성 증대

8. ./data/result_out 폴더에 각각 결과 데이터 저장
--> 바뀐점 : 장기,단기 테이블같이 현재 안쓰는 테이블의 경우 구하지않고 현재 사용되는 info_result_out과 graph_result_out테이블만 생성


### 배경

 *네이버 검색어트랜드 API를 통해 금융권에서 자주쓰이는 검색어들의 연관검색어 및 연관검색어들의 일별,주별,월별 트랜드를 분석하는 프로젝트

* 대용량 데이터 분석과 처리 과정에서 순차적 실행 로직이 성능 저하와 비효율적인 데이터관리가 주된 원인이었음

* 이러한 문제를 해결하기 위해, 우리는 프로세스의 동시 실행이 가능한 비동기 프로그래밍 모델을 도입하고, 코드의 재사용성을 높이며 중복을 최소화하고 가독성이 높아지는 방향으로 코드를 재구성함

### 기술적 도전과 해결책

**동시성 프로그래밍 적용**: `asyncio`를 활용하여 I/O 바운드 작업의 병렬 처리를 구현함으로써, 전체 작업의 완료 시간을 단축시킴

--> 사례)
    1. 구글 트렌드 분석 개선: 원래 구글 트렌드 데이터 분석 로직은 동기적 프로그래밍 모델을 사용하여 개별 요청을 순차적으로 처리하였음. 이로 인해, 대량의 데이터 요청 시 처리 시간이 길어지는 문제가 있었음. asyncio를 도입하여 동시에 여러 데이터 요청을 처리할 수 있도록 로직을 개선한 결과, 전체 분석 시간을 기존 대비 약 90% 단축시킬 수 있었음. 이는 동시 요청 처리가 가능해짐으로써 데이터 수집 및 분석의 효율성이 크게 증가했음을 의미함.


    2. 네이버 블로그/뉴스 데이터 호출 최적화: 네이버 블로그와 뉴스 데이터를 호출하는 기존 동기적 프로그래밍 방식은 한 번에 하나의 요청만 처리할 수 있어, 데이터 수집에 상당한 시간이 소요되었음. 비동기 프로그래밍 방식으로 전환함으로써, 여러 요청을 동시에 처리할 수 있게 되었고, 이는 데이터 수집 시간을 약 90% 줄이는 결과를 가져왔음. 또한, 이 변화는 데이터 호출 로직의 오류 발생률을 낮추는 부수적인 효과도 가져왔음.


    3. 네이버 데이터랩 트렌드 분석 효율성 향상: 네이버 데이터랩을 사용한 트렌드 분석 작업 또한 비동기 프로그래밍 모델을 적용하여 성능을 개선함. 복수의 키워드에 대한 트렌드 데이터를 병렬로 요청하고 처리하게 함으로써, 전체적인 데이터 분석 작업에 할당되는 시간을 기존 대비 90% 이상 감소시킴. 이 개선을 통해, 외부트렌드 분석의 자동화에 대한 비용이 현저히 떨어질 것으로 보임.


 **코드 최적화**: 중복된 데이터 처리 로직을 함수로 분리하고, 불필요한 반복문을 제거하여 코드의 실행 효율성을 향상시킴

--> 사례)
    1. 보안 및 자동화 대비: 이전에는 팀의 네이버 API id와 pw가 코드 내에 하드코딩되어 있어, 자동화 과정에서 보안상의 문제가 발생할 가능성이 농후함. 이를 해결하기 위해 secrets.json 파일을 도입하여 API 키를 외부에서 안전하게 관리하게 함으로써, 자동화 과정을 구현하는 동시에 보안을 강화함.


    2. 메모리 사용량 및 속도 최적화: 초기 접근 방식에서는 Jupyter Notebook의 특성을 활용하여 데이터 분석을 위해 CSV 파일 형태로 데이터를 저장하고 처리하였음. 이 방법은 대규모 데이터셋 처리 시 메모리 사용량이 증가하고, 속도가 저하되는 단점이 있었음. 문제를 해결하기 위해, 모든 데이터 처리 과정을 DataFrame을 사용하여 메모리 내에서 직접 수행하도록 변경하였으며 중간에 끊기는 위험을 대비하여 중간마다 데이터는 csv로 한개의 파일로 관리하여 중요한 처리 단계마다 데이터를 CSV 파일 형태로 백업함으로써 데이터 손실 리스크를 최소화하였음. 이로 인해 데이터 처리 속도가 크게 개선되었고, 메모리 사용량도 줄어들었음.


    3. 중복 계산 및 저장 제거: 데이터 분석 과정에서 트렌드 데이터와 그래프 생성에 필요한 정보를 중복해서 계산하거나 저장하는 비효율적인 코드가 발견되었음. 이러한 중복을 제거함으로써, 코드의 실행 시간을 단축시키고, 메모리 사용량을 줄일 수 있었음. 또한, 코드의 가독성과 유지 보수성이 향상되었음.


    4. 함수의 통합과 재구성 : 비슷한 기능을 수행하는 여러 함수가 발견되었음. 이 함수들을 통합하고 재구성함으로써, 코드의 중복을 최소화하고, 유지 보수성을 개선함. 이러한 구조적 개선을 통해, 향후 코드 변경이나 기능 추가 시 발생할 수 있는 오류의 가능성을 줄이고, 개발 팀의 작업 효율성을 높일 수 있음.

    5. 다양한 경우에서의 예외처리를 통해 코드의 안정성을 높임

### 성과 및 결과

이러한 개선 작업을 통해, 처리 시간을 기존의 5시간에서 40분 미만으로 줄일 수 있었음(약 20~30분 소요)

## 개선가능성

1. 대부분의 코드들이 독립적으로 돌아가는 형식이기 때문에 병렬적구조를 통해 시간을 더 줄일 가능성 존재

2. github actions 을 이용해서 매일 밤 일정한 시간에 이 코드들을 돌아가게 만든 이후 아침마다 업로드를 하는 방식을 통해 회사에서 외부트렌드를 위해 할당하는 시간을 업로드를 하는 시간으로 바꿀 가능성이 존재

3. 이후 api제한할당을 해제하면서(naver api 제휴를 통해 api 제한을 풀 수 있음) api할당때문에 생기는 오류를 해결할 수 있음