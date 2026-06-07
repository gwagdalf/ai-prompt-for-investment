# FnGuide 재무 데이터 크롤러 생성을 위한 프롬프트

## 1. 전체 목표

finance.yahoo.com 웹사이트에서 여러 주식 종목의 재무 컨센서스 데이터를 스크래핑하고, 그 결과를 단일 CSV 파일로 저장하는 Python 스크립트 @crawl_yahoo.py 를 작성해 주세요.
@crawl_fnguide.py 를 참고하여 작성하세요 

## 2. 주요 기능

- 스크립트는 미리 정의된 주식 코드 목록을 처리할 수 있어야 합니다.
- 주요 재무 지표(Revenue, EPS, BPS, DPS, Average Taget Price)를 스크래핑해야 합니다.
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

1.  **주식 코드 정의**: 이 블록 안에 스크래핑할 종목 코드를 담은 `STOCK_CODES`라는 이름의 리스트를 생성합니다 (예: `"AAPL"`, `"NVDA"`).
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

2.  **Yahoo finance 페이지로 이동**:
    - URL을 구성합니다: `f"https://finance.yahoo.com/quote/{stock_code}/financials/"`
    - `driver.get()`을 사용하여 페이지를 로드하고 몇 초간 기다립니다.
    - `driver.page_source`로부터 `BeautifulSoup` 객체를 생성합니다.

3.  **회사 이름 추출**:
    - 회사이름을 추출합니다 예 <h1 class="heading yf-ndxd9a">Apple Inc. (AAPL)</h1> 에서 Apple Inc. 를 추출
    - 텍스트를 가져와 `results['company']`에 저장합니다.

4.  **재무 예측치 추출 (Revenue, EPS, BPS, DPS)**:
    
Revenue 추출
12/31/2024 에 해당하는 revenue 를 추출하여 Revenue(B)2024/12 에 저장합니다
12/31/2025 에 해당하는 revenue 를 추출하여 Revenue(B)2025/12 에 저장합니다 

EPS 추출
12/31/2024 에 해당하는 EPS 를 추출하여 eps2024/12 에 저장합니다
12/31/2025 에 해당하는 revenue 를 추출하여 eps2025/12 에 저장합니다 

대상영역 : <div class="row lv-0 yf-1duawpp"><div class="column sticky yf-1duawpp"> <div class="rowTitle yf-1duawpp" title="Basic EPS">Basic EPS</div></div> <div class="column yf-1duawpp alt">13.24 </div><div class="column yf-1duawpp">10.91 </div><div class="column yf-1duawpp alt">8.13 </div><div class="column yf-1duawpp">5.84 </div><div class="column yf-1duawpp alt">4.59 </div></div>

BPS 추출
https://finance.yahoo.com/quote/{stock_code}/key-statistics/ 페이지로 이동합니다. 

Price/Book 의 current 값을 수집하여 bps2026/12 에 저장합니다
Price/Book 의 12/31/2025	9/30/2025	6/30/2025	3/31/2025 의 값을 구하여 평균 값을 bps2025/12 에 저장합니다
대상영역 : <tr class="yf-1omhm64 alt"><td class="yf-1omhm64">Price/Book</td> <td class="yf-1omhm64">9.39</td><td class="yf-1omhm64">8.39</td><td class="yf-1omhm64">9.78</td><td class="yf-1omhm64">8.09</td><td class="yf-1omhm64">6.18</td><td class="yf-1omhm64">5.78</td> </tr>

Forward Annual Dividend Rate 값을 수집하여 dps2026/12 에 저장합니다



DPS 추출
변수
{past_5y_timestamp} : 5년 전 날짜의 timestamp 값
{now_timestamp} : 오늘 날짜의 timestamp 값
{stock_code} : 주식코드
https://finance.yahoo.com/quote/{stock_code}/history/?filter=div&frequency=1mo&period1={past_5y_timestamp}&period2={past_5y_timestamp}  페이지로 이동합니다
예: https://finance.yahoo.com/quote/AAPL/history/?period1=1623030938&period2=1780797336&frequency=1mo&filter=div

2025 년도 배당금액을 추출하고 합산하여,dps2025/12 에 기록하세요 
2024 년도 배당금액을 추출하고 합산하여,dps2024/12 에 기록하세요

대상영역 : <table class="table yf-u4m6f0 noDl hideOnPrint"><thead class="yf-u4m6f0"><tr class="yf-u4m6f0"><th class="yf-u4m6f0">Date</th> <th class="center yf-u4m6f0">Dividend <span class="container yf-1aqyc8a"><div aria-hidden="true" class="icon fin-icon primary-icn sz-medium tw-align-text-top yf-15ilbqr"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2m0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8"></path></svg></div> <div class="tooltip al-bottom   yf-1aqyc8a" role="tooltip"><div class="arrow yf-1aqyc8a"></div>   <span class="toolTipContent yf-u4m6f0" slot="content">Dividends on any given ex-date include regular and any special dividends</span></div> </span></th></tr></thead> <tbody><tr class="yf-u4m6f0"><td class="yf-u4m6f0">May 11, 2026</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.27</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Feb 9, 2026</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.26</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Nov 10, 2025</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.26</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Aug 11, 2025</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.26</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">May 12, 2025</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.26</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Feb 10, 2025</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.25</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Nov 8, 2024</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.25</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Aug 12, 2024</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.25</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">May 10, 2024</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.25</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Feb 9, 2024</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.24</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Nov 10, 2023</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.24</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Aug 11, 2023</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.24</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">May 12, 2023</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.24</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Feb 10, 2023</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.23</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Nov 4, 2022</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.23</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Aug 5, 2022</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.23</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">May 6, 2022</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.23</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Feb 4, 2022</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.22</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Nov 5, 2021</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.22</span> Dividend </td> </tr><tr class="yf-u4m6f0"><td class="yf-u4m6f0">Aug 6, 2021</td> <td colspan="6" class="event yf-u4m6f0"><span class="yf-u4m6f0">0.22</span> Dividend </td> </tr></tbody></table>


Analysis 추출
https://finance.yahoo.com/quote/{stock_code}}/analysis/ 로 이동합니다. 
예 : https://finance.yahoo.com/quote/AAPL/analysis/

Revenue vs. Earnings 옆의 Annual 을 선택하여 yearly 데이터로 변경합니다. 참고 <input type="checkbox" id="swc-uhm5vqt6" data-ylk="elm:ct;elmt:btn;itc:1;sec:button;slk:yearly" data-yga="{&quot;yLinkElement&quot;:&quot;ct&quot;,&quot;yLinkElementType&quot;:&quot;btn&quot;,&quot;yModuleName&quot;:&quot;button&quot;,&quot;yLinkText&quot;:&quot;yearly&quot;}" class="yf-fzko74" value="yearly" data-rapid_p="33" data-y-link-id="1ecbd0o0nnc4z20wl6gn" data-v9y="1">

Revenue Estimate 의 
Current Year (2026)	 의 Avg. Estimate 추출하여  Revenue(B)2026/12 에 저장합니다
Next Year (2027)	 의 Avg. Estimate 추출하여  Revenue(B)2027/12 에 저장합니다
대상영역 : <div class="tableContainer yf-1rzyz4n"><div data-testid="data-table-v2" class="table-container cs-regular yf-1hgjbtd altShading"><table class="yf-1hgjbtd bd"><thead class="yf-1hgjbtd"><tr class="yf-1hgjbtd"><th data-testid-header="label" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Currency in USD</div></th><th data-testid-header="0q" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Current Qtr. (Jun 2026)</div></th><th data-testid-header="+1q" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Next Qtr. (Sep 2026)</div></th><th data-testid-header="0y" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Current Year (2026)</div></th><th data-testid-header="+1y" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Next Year (2027)</div></th> </tr></thead> <tbody><tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="0"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">No. of Analysts </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">37 </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">33 </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">52 </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">53 </td></tr> <tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="1"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">Avg. Estimate </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">116.63B </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">123.33B </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">487.04B </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">577.53B </td></tr> <tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="2"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">Low Estimate </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">113.62B </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">119.06B </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">473.89B </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">475.29B </td></tr> <tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="3"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">High Estimate </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">120.13B </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">135.93B </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">518.97B </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">674.24B </td></tr> <tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="4"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">Year Ago Sales </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">96.43B </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">102.35B </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">402.84B </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">487.04B </td></tr> <tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="5"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">Sales Growth (year/est) </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">20.95% </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">20.50% </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">20.90% </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">18.58% </td></tr> </tbody> <tfoot class="yf-1hgjbtd"><tr class="yf-1hgjbtd"> </tr></tfoot></table> </div> </div>

Earnings Estimate 의 
Current Year (2026)	 의 Avg. Estimate 추출하여  Revenue(B)2026/12 에 저장합니다
Next Year (2027)	 의 Avg. Estimate 추출하여  Revenue(B)2027/12 에 저장합니다
대상영역 : <table class="yf-1hgjbtd bd"><thead class="yf-1hgjbtd"><tr class="yf-1hgjbtd"><th data-testid-header="label" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Currency in USD</div></th><th data-testid-header="0q" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Current Qtr. (Jun 2026)</div></th><th data-testid-header="+1q" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Next Qtr. (Sep 2026)</div></th><th data-testid-header="0y" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Current Year (2026)</div></th><th data-testid-header="+1y" class=" yf-1hgjbtd"><div class="colCont yf-1hgjbtd"> Next Year (2027)</div></th> </tr></thead> <tbody><tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="0"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">No. of Analysts </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">43 </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">38 </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">52 </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">55 </td></tr> <tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="1"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">Avg. Estimate </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">2.87 </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">3 </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">14.24 </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">14.43 </td></tr> <tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="2"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">Low Estimate </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">2.6 </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">2.67 </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">12.79 </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">11.7 </td></tr> <tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="3"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">High Estimate </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">3.13 </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">3.72 </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">15.13 </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">17.18 </td></tr> <tr class="row yf-1hgjbtd" data-testid="data-table-v2-row" data-testid-row="4"><td data-testid-cell="label" class=" yf-1hgjbtd" style="--_depth: false;">Year Ago EPS </td><td data-testid-cell="0q" class=" yf-1hgjbtd" style="--_depth: false;">2.31 </td><td data-testid-cell="+1q" class=" yf-1hgjbtd" style="--_depth: false;">2.87 </td><td data-testid-cell="0y" class=" yf-1hgjbtd" style="--_depth: false;">10.81 </td><td data-testid-cell="+1y" class=" yf-1hgjbtd" style="--_depth: false;">14.24 </td></tr> </tbody> <tfoot class="yf-1hgjbtd"><tr class="yf-1hgjbtd"> </tr></tfoot></table>



https://finance.yahoo.com/quote/{stock_code}}/ 로 이동하세요
Analyst Price Targets low 값을 수집하여 적정주가Min 에 저장하세요
Analyst Price Targets high 값을 수집하여 적정주가Max 에 저장하세요
Analyst Price Targets average 값을 수집하여 적정주가Consensus 에 저장하세요
대상영역 : <a class="card-link yf-1utw0yo" href="/quote/AAPL/analyst-insights/" title="Analyst Price Targets" aria-label="Analyst Price Targets" data-ylk="elm:navcat;elmt:link;itc:0;sec:qsp-analyst-price-target;slk:qsp-analyst-price-target-analysis" data-yga="{&quot;yLinkElement&quot;:&quot;navcat&quot;,&quot;yLinkElementType&quot;:&quot;link&quot;,&quot;yModuleName&quot;:&quot;qsp-analyst-price-target&quot;,&quot;yLinkText&quot;:&quot;qsp-analyst-price-target-analysis&quot;}" data-rapid_p="555" data-y-link-id="060vfxu065aefj0lyk91" data-v9y="1">&nbsp;</a>

Beta (5Y Monthly) 값을 수집하여, beta 에 저장하세요  
대상영역 : <li class=" yf-13utneb"><span class="label yf-13utneb" title="Beta (5Y Monthly)">Beta (5Y Monthly) </span> <span class="value yf-13utneb">1.09</span> </li>



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
