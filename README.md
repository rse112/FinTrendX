# FinTrendX

## 프로젝트 개요
이 프로젝트는 특정 메인 키워드에 대한 연관 검색어, 트렌드 데이터, 뉴스 데이터, 블로그 데이터를 수집하고 분석하여 급상승, 지속상승, 규칙성을 보이는 데이터를 분류하는 것을 목적으로 합니다.

## 프로젝트 구조
1. 메인키워드별 연관검색어 집계
2. 각 키워드별 트렌드데이터 집계
3. 선별함수를 통한 급상승/지속상승/규칙성 데이터 분류
4. 네이버 뉴스데이터/구글검색어 데이터 집계 (비고: 구글검색어 데이터는 api 자체 오류 다분)
5. 블로그데이터를 통한 활동성 데이터 집계
6. merge

## 설치 및 실행 방법
1. 이 저장소를 클론합니다:
    ```bash
    git clone https://github.com/rse112/rse112.github.io.git
    ```
2. 필요한 의존성을 설치합니다:
    ```bash
    pip install -r requirements.txt
    ```
3. `REALDATA.ZIP` 파일을 COLAB에 업로드합니다.
4. 프로젝트를 실행합니다 (09시 이후):
    ```bash
    python main.py
    ```

## 결과물
- 결과 페이지: [https://trendkey-7a41071967af.herokuapp.com/](https://trendkey-7a41071967af.herokuapp.com/)
- 깃허브 저장소: [https://github.com/rse112/rse112.github.io](https://github.com/rse112/rse112.github.io)

<img src="https://github.com/user-attachments/assets/0a838bd9-6a99-4dde-b44f-eb589069535b" alt="트렌드 분석 결과 차트" width="600"/>

**[그림 1]** 트렌드 분석 결과 시각화
## 주의사항
1. 반드시 09시 이후에 실행할 것 (API 업데이트가 9시 정각에 이루어짐)
2. COLAB에 `REALDATA.ZIP` 파일을 올려서 실행

## 기여 방법
1. 이 저장소를 포크합니다.
2. 새로운 브랜치를 생성합니다:
    ```bash
    git checkout -b feature/new-feature
    ```
3. 변경 사항을 커밋합니다:
    ```bash
    git commit -m 'Add new feature'
    ```
4. 브랜치에 푸시합니다:
    ```bash
    git push origin feature/new-feature
    ```
5. 풀 리퀘스트를 생성합니다.
