# FnGuide 재무 데이터 크롤러 생성을 위한 프롬프트

## 1. 전체 목표

FnGuide 웹사이트에서 여러 대한민국 주식 종목의 재무 컨센서스 데이터를 스크래핑하고, 그 결과를 단일 CSV 파일로 저장하는 Python 스크립트를 작성해 주세요.

## 2. 주요 기능

- 스크립트는 미리 정의된 주식 코드 목록을 처리할 수 있어야 합니다.
- 주요 재무 지표(매출액, EPS, BPS, DPS, 목표주가)를 스크래핑해야 합니다.
- 모든 종목에서 수집된 데이터는 동적으로 생성된 이름의 단일 CSV 파일에 취합되어 저장되어야 합니다.
- 스크립트는 단일 종목의 오류에 대해 안정적이어야 하며, 나머지 종목들의 처리를 계속할 수 있어야 합니다.
- 웹 페이지 탐색에는 `selenium`을, HTML 파싱에는 `BeautifulSoup`을 사용해야 합니다.

## 3. 필요 라이브러리

스크립트에는 다음 Python 라이브러리가 필요합니다. 필요한 import 구문을 포함해 주세요.

- `os`
- `csv`
- `time`
- `datetime` (from `datetime`)
- `webdriver` (from `selenium`)
- `Service` (from `selenium.webdriver.chrome.service`)
- `Options` (from `selenium.webdriver.chrome.options`)
- `ChromeDriverManager` (from `webdriver_manager.chrome`)
- `BeautifulSoup` (from `bs4`)

---

## 4. 단계별 구현 세부 정보

다음 단계에 따라 스크립트를 구현해 주세요.

### 1단계: 메인 실행 블록

스크립트 하단에 `if __name__ == "__main__":` 블록을 생성합니다.

1.  **주식 코드 정의**: 이 블록 안에 스크래핑할 종목 코드를 담은 `STOCK_CODES`라는 이름의 리스트를 생성합니다 (예: `"005930"`, `"000660"`).
2.  **데이터 취합**: `all_data`라는 이름의 빈 리스트를 초기화합니다.
3.  **반복 및 스크래핑**: `STOCK_CODES`의 각 `code`를 반복합니다. 각 반복에서 어떤 코드가 처리 중인지 알리는 메시지를 출력하고, 메인 데이터 수집 함수(예: `get_stock_data(code)`)를 호출한 뒤, 반환된 데이터 딕셔너리를 `all_data` 리스트에 추가합니다.
4.  **데이터 저장**: 반복이 끝나면, 수집된 모든 데이터를 파일에 쓰기 위해 저장 함수(예: `save_to_csv(all_data)`)를 호출합니다.

### 2단계: WebDriver 설정 함수

Selenium WebDriver를 초기화하고 반환하는 `setup_driver()` 함수를 생성합니다.

- `--headless` 모드로 실행되도록 `ChromeOptions`를 설정해야 합니다.
- 드라이버를 자동으로 관리하기 위해 `webdriver_manager.chrome.ChromeDriverManager`를 사용합니다.

### 3단계: 핵심 데이터 스크래핑 함수 (`get_stock_data`)

이 함수는 `stock_code`를 입력으로 받아 해당 주식에 대해 스크래핑된 모든 데이터를 담은 딕셔너리를 반환합니다.

1.  **초기화**:
    - `setup_driver()`를 호출하여 드라이버 인스턴스를 가져옵니다.
    - 결과 딕셔너리를 초기화합니다: `results = {"code": stock_code}`.
    - `driver.quit()`가 항상 호출되도록 전체 프로세스를 `try...finally` 블록으로 감쌉니다.

2.  **컨센서스 페이지로 이동**:
    - URL을 구성합니다: `f"https://comp.fnguide.com/SVO2/ASP/SVD_Consensus.asp?pGB=1&gicode=A{stock_code}"`
    - `driver.get()`을 사용하여 페이지를 로드하고 몇 초간 기다립니다.
    - `driver.page_source`로부터 `BeautifulSoup` 객체를 생성합니다.

3.  **회사 이름 추출**:
    - `id="giName"`을 가진 `<h1>` 태그를 찾습니다.
    - 텍스트를 가져와 `results['company']`에 저장합니다.

4.  **재무 예측치 추출 (매출액, EPS, BPS, DPS)**:
    - **대상 영역**: 데이터는 `id="bodycontent1"`을 가진 `<div>` 내에 있습니다.
    - **로직**: 각 지표의 데이터는 별도의 `<tr>`에 있습니다. 제목으로 올바른 행을 찾은 다음, 후속 `<td>` 셀에서 값을 추출해야 합니다.
    - **상세 단계**:
        - `#bodycontent1`의 메인 테이블 `<tbody>` 바로 아래에 있는 모든 `<tr>` 요소를 찾습니다.
        - 이 행들을 반복합니다:
            - 각 행에 대해 `<th>` 텍스트에 "매출액"이 포함되어 있는지 확인합니다.
            - 만약 포함되어 있다면, 해당 행의 모든 `<td>` 요소를 찾습니다. 2024-2027년 예측값은 일반적으로 인덱스 1에서 4에 있습니다.
            - 각 `<td>`에서 텍스트 값을 파싱합니다. 쉼표와 하이픈을 처리하기 위해 헬퍼 함수 `parse_value()`를 사용합니다 (예: "1,234" -> 1234.0, "-" -> 0).
            - "매출액"의 경우, 파싱된 값을 10000으로 나누어 '조원' 단위로 변환합니다.
            - 결과를 `'매출액(조원)2024/12'`와 같은 키를 사용하여 딕셔너리에 저장합니다.
        - "EPS", "BPS", "DPS"에 대해서도 동일한 로직을 반복합니다 (10000으로 나누지 않음).

5.  **목표주가 추출**:
    - **대상 영역**: 데이터는 `id="bodycontent3"`을 가진 `<div>` 내에 있습니다.
    - **로직**: 컨센서스 가격을 가져오고, 모든 분석가의 목표주가로부터 최소/최대값을 계산해야 합니다.
    - **상세 단계**:
        - **컨센서스 가격**: `class="tbody_tit2"`를 가진 `<tr>`을 찾습니다. 컨센서스 가격은 이 행의 3번째 `<td>`에 있습니다. 이를 파싱하여 `results['적정주가Consensus']`로 저장합니다.
        - **최소/최대 가격**:
            - `prices`라는 빈 리스트를 초기화합니다.
            - 목표주가 테이블의 모든 `<tr>` 요소를 찾습니다.
            - 각 행에 대해 3번째 `<td>`에서 값을 파싱합니다.
            - 파싱된 값이 0보다 크면 `prices` 리스트에 추가합니다.
            - 모든 행을 반복한 후, `prices` 리스트가 비어있지 않으면 `max(prices)`와 `min(prices)`를 계산합니다. 이를 `results['적정주가Max']`와 `results['적정주가Min']`으로 저장합니다.

6.  **베타 추출**:
    - 지금은 이 값을 동적으로 스크래핑할 필요가 없습니다. 결과 딕셔너리에 하드코딩된 값을 추가하기만 하면 됩니다: `results['beta'] = 1.8`.

7.  **오류 처리**:
    - 스크래핑 로직을 `try...except Exception as e` 블록으로 감쌉니다. 오류가 발생하면(예: 페이지가 로드되지 않거나 요소를 찾을 수 없음), 오류를 출력하고 스크립트가 중단되지 않도록 `results` 딕셔너리를 기본값(0 또는 'Error')으로 채웁니다.

8.  **반환 값**: 함수는 `results` 딕셔너리를 반환해야 합니다.

### 4단계: CSV 저장 함수 (`save_to_csv`)

이 함수는 데이터 딕셔너리의 리스트(`data_list`)를 입력으로 받습니다.

1.  **빈 데이터 처리**: `data_list`가 비어 있으면 메시지를 출력하고 반환합니다.
2.  **파일명 생성**:
    - 현재 타임스탬프를 가져옵니다: `now = datetime.now().strftime("%Y%m%d-%H%M%S")`.
    - 첫 번째 데이터 항목을 가져옵니다: `first_data = data_list[0]`.
    - 파일명을 생성합니다: `f"fnguide-{first_data['company']}포함{len(data_list)}개-{first_data['code']}-{now}.csv"`.
3.  **헤더 정의**: 원하는 순서대로 정확한 열 이름을 담은 `header` 리스트를 생성합니다.
4.  **CSV에 쓰기**:
    - 생성된 파일명을 쓰기 모드(`'w'`)로 열고, `newline=''`과 `encoding='utf-8-sig'`를 설정합니다.
    - `csv.DictWriter` 객체를 생성합니다.
    - `writer.writeheader()`를 사용하여 헤더를 씁니다.
    - `writer.writerows(data_list)`를 사용하여 모든 데이터 행을 씁니다.
    - 파일이 저장되었다는 확인 메시지를 출력합니다.
