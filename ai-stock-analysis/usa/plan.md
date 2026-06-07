# Plan — `crawl_yahoo.py` 기술 구현 계획

> **무엇을(What)** 은 `spec.md`, **원칙** 은 `constitution.md` 참조. 이 문서는 **어떻게(How)**.

---

## 1. 아키텍처 개요

`crawl_fnguide.py` 와 동일한 절차적 단일 파일 구조. 종목당 5개 페이지를 순차 방문.

```
main
 └─ for code in STOCK_CODES
       └─ get_stock_data(code)            # 종목당 1 드라이버 (try/finally)
             ├─ _scrape_financials(...)    # 4.1  company, Revenue/EPS 2024·2025
             ├─ _scrape_analysis(...)      # 4.2  Revenue/EPS 2026·2027 추정
             ├─ _scrape_key_statistics(...)# 4.3  bps 2025·2026, dps 2026
             ├─ _scrape_dividends(...)     # 4.4  dps 2024·2025
             └─ _scrape_quote(...)         # 4.5  적정주가, beta
 └─ save_to_csv(all_data)
```

> 헬퍼 분리는 권장(가독성/테스트성). 단순화를 위해 `get_stock_data` 내 인라인 블록으로 둬도 무방하나, 페이지별 `try/except` 로 부분 실패를 격리할 것.

## 2. 라이브러리 / 기술 스택

`crawl_fnguide.py` 와 동일:
```python
import os, csv, time
from datetime import datetime, timedelta   # timedelta: 5년 전 timestamp 계산용 추가
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
```
> Yahoo 동적 렌더링 대비 `WebDriverWait` / `expected_conditions` 사용을 권장(선택).

## 3. 공통 함수

### 3.1 `setup_driver()`
- `crawl_fnguide.py` 그대로 재사용: `--headless`, `--no-sandbox`, `--disable-dev-shm-usage`, 30s timeout.
- (선택) `--lang=en-US`, User-Agent 지정으로 영문 페이지 고정.

### 3.2 `parse_value(value_str)` — **Yahoo 대응 확장**
FnGuide 버전은 콤마만 처리. Yahoo 는 단위 접미사가 있으므로 확장:
- `"487.04B"` → `487.04` (B 제거, 이미 십억 단위)
- `"577.53M"` → `0.57753` (백만 → 십억 환산, **Revenue 전용**) — 또는 호출부에서 스케일 처리
- `"20.95%"` → `20.95` (% 제거)
- `"-"`, `""`, `"N/A"` → `0`
- 콤마/공백/통화기호 제거 후 `float`
- 변환 실패 시 `0` 반환(예외 던지지 않음).

> 권장: `parse_value` 는 순수 숫자화만 담당하고, **B/M 단위 환산은 명시적 헬퍼**(`parse_revenue_b()`)로 분리해 혼동 방지.

## 4. 페이지별 파싱 전략 (견고한 셀렉터)

### 4.1 financials
- 회사명: `soup.find('h1')` 텍스트 → `" (" 기준 split[0].strip()`.
- 테이블: `div.row` 들 중 `rowTitle[title="..."]` 또는 텍스트로 행 식별.
  - `Total Revenue`, `Basic EPS` 행 탐색.
- 컬럼 매핑: thead 의 날짜 헤더(`12/31/2024`, `12/31/2025` …)를 읽어 **인덱스를 동적으로** 결정. 고정 인덱스 지양(연도 위치가 분기별로 밀릴 수 있음).
- Revenue 는 원시값이 절대금액 → **십억(B) 단위로 환산** 후 저장.

### 4.2 analysis
- `Revenue Estimate` / `Earnings Estimate` 두 테이블 구분: 헤더 인접 라벨 또는 출현 순서.
- 컬럼은 `data-testid-header` 의 `0y`(Current Year), `+1y`(Next Year) 사용 → **연도 텍스트(2026/2027)로 검증**.
- 행은 `td[data-testid-cell="label"]` 텍스트가 `"Avg. Estimate"` 인 행 선택.
- Revenue → `parse_value`("...B") 후 십억 단위 그대로 저장. EPS → 숫자 그대로.

### 4.3 key-statistics
- `Price/Book` 행: `td` 텍스트 `"Price/Book"` 매칭 후 형제 `td` 들 수집.
  - 첫 값 = Current → `bps2026/12`.
  - 이후 분기 컬럼(헤더의 `12/31/2025, 9/30/2025, 6/30/2025, 3/31/2025`)에 해당하는 값 4개 평균 → `bps2025/12`.
  - ⚠️ 헤더의 날짜 위치를 읽어 매핑(고정 인덱스 금지).
- `Forward Annual Dividend Rate` 행 → `dps2026/12`.

### 4.4 history (dividends)
- timestamp:
  ```python
  now_ts = int(time.time())
  past_5y_ts = int((datetime.now() - timedelta(days=5*365)).timestamp())
  ```
- URL: `.../history/?filter=div&frequency=1mo&period1={past_5y_ts}&period2={now_ts}`
- 테이블 각 행: `td[0]` = 날짜(`"May 11, 2026"`), `td.event > span` = 배당액.
- 날짜에서 **연도 파싱**(`datetime.strptime(date, "%b %d, %Y").year`) 후 연도별 합산.
  - 2025 합 → `dps2025/12`, 2024 합 → `dps2024/12`.

### 4.5 quote (메인)
- Analyst Price Targets: Low/Average/High 수치. 카드 영역에서 라벨 인접 값 또는 `data-testid` 로 추출.
  - 클래스 해시 의존 금지 → 텍스트 라벨("Low"/"Average"/"High") 기반.
- `Beta (5Y Monthly)`: `<span class="label" title="Beta (5Y Monthly)">` 형제 `span.value` → `beta`.
  - `title` 속성(`title="Beta (5Y Monthly)"`)으로 안정적으로 찾음.

## 5. 오류 처리 전략

- `get_stock_data`: 전체를 `try/except Exception` + `finally: driver.quit()`.
- **페이지별 부분 격리:** 각 `_scrape_*` 블록을 개별 `try/except` 로 감싸 한 페이지 실패가 다른 페이지 수집을 막지 않게 함.
- 종료 시 `results.setdefault(key, 0)` 로 모든 헤더 키를 보장(누락 시 CSV 오류 방지).

## 6. `save_to_csv(data_list)`

- `crawl_fnguide.py` 와 동일 로직. 차이점:
  - 파일명 접두사 `yahoo-`.
  - `header` 는 spec §5 의 고정 컬럼.

## 7. `__main__`

- `STOCK_CODES` 미국 티커 리스트(예: `["AAPL", "NVDA", ...]`).
- 종목 루프 + 진행 로그 + `save_to_csv`.

## 8. 위험 요소 (Risks)

| 위험 | 영향 | 완화 |
|---|---|---|
| Yahoo 클래스 해시 변경 | 셀렉터 깨짐 | 텍스트/`data-testid` 기반(Art.3) |
| 동적 렌더링 지연 | 빈 값 수집 | `WebDriverWait` 또는 충분한 `sleep` |
| 쿠키/GDPR 동의 배너 | 파싱 실패 | 배너 수락 시도 후 진행 |
| 분기 컬럼 위치 변동 | 잘못된 연도 매핑 | 헤더 날짜 텍스트로 동적 인덱싱 |
| Rate limiting | 차단 | 순차 처리 + 페이지 간 대기 |
| 단위 혼동(B/M/절대값) | Revenue 스케일 오류 | `parse_revenue_b()` 분리, 인수기준 #4 검증 |
