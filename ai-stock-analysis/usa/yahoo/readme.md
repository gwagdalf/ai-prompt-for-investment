# Yahoo Finance Financial Data Crawler

## 1. 개요

`crawl_yahoo.py`는 [finance.yahoo.com](https://finance.yahoo.com)에서 미국 상장 종목의 재무 컨센서스 데이터를 자동으로 수집하여 단일 CSV 파일로 저장하는 파이썬 스크립트입니다.

`crawl_fnguide.py`(한국 종목)와 동일한 코드 구조·출력 스키마를 따르므로, 두 크롤러의 결과를 동일한 투자 분석 시트에서 병합하여 사용할 수 있습니다.

결과 예

---

## 2. 수집 데이터

종목당 Yahoo Finance 5개 페이지에서 아래 지표를 수집합니다.

| 지표 | 컬럼명 | 출처 페이지 |
|---|---|---|
| 기업명 | `company` | `/financials/` |
| 종목 코드 | `code` | 입력값 |
| 매출액(십억$) | `Revenue(B)2024/12` ~ `2027/12` | `/financials/`, `/analysis/` |
| 주당순이익 | `eps2024/12` ~ `eps2027/12` | `/financials/`, `/analysis/` |
| 주당순자산 | `bps2025/12`, `bps2026/12` | `/key-statistics/` |
| 주당배당금 | `dps2024/12` ~ `dps2026/12` | `/history/`, `/key-statistics/` |
| 적정주가 | `적정주가Min`, `적정주가Consensus`, `적정주가Max` | `/analyst-insights/` |
| 베타(5Y월간) | `beta` | 메인 quote 페이지 |

---

## 3. 사전 준비

#### 라이브러리 설치

```bash
pip install selenium webdriver-manager beautifulsoup4
```

#### Chrome 브라우저 설치

Chrome이 설치되어 있어야 합니다. `webdriver-manager`가 ChromeDriver를 자동으로 관리합니다.

---

## 4. 사용 방법

### 1단계 — 종목 코드 수정

`crawl_yahoo.py` 하단의 `STOCK_CODES` 리스트에 수집할 미국 티커를 입력합니다.

```python
if __name__ == "__main__":
    STOCK_CODES = [
        "AAPL",   # Apple
        "NVDA",   # NVIDIA
        "MSFT",   # Microsoft
        # 원하는 티커를 추가 ...
    ]
```

### 2단계 — 스크립트 실행

```bash
cd ai-stock-analysis/usa/yahoo
python crawl_yahoo.py
```

실행 중 아래와 같은 진행 로그가 출력됩니다.

```
데이터 수집 시작: AAPL...
  -> financials: https://finance.yahoo.com/quote/AAPL/financials/
  -> analysis: https://finance.yahoo.com/quote/AAPL/analysis/
  -> key-statistics: https://finance.yahoo.com/quote/AAPL/key-statistics/
  -> history/dividends: AAPL
  -> analyst-insights: https://finance.yahoo.com/quote/AAPL/analyst-insights/
  -> quote main (beta): https://finance.yahoo.com/quote/AAPL/
  beta=1.24, targets Low=150.0 Avg=225.0 High=300.0
```

### 3단계 — 결과 확인

수집이 완료되면 `output/` 디렉토리에 CSV 파일이 저장됩니다.

```
output/yahoo-Apple Inc.포함3개-AAPL-20260607-130000.csv
```

파일명 형식: `yahoo-{첫번째기업명}포함{총개수}개-{첫번째티커}-{YYYYMMDD-HHMMSS}.csv`

CSV는 `utf-8-sig` 인코딩으로 저장되어 Excel에서 한글 깨짐 없이 열립니다.

---

## 5. 오류 처리

한 종목의 수집이 실패해도 나머지 종목은 계속 처리됩니다. 실패한 종목은 `company='Error'`, 수치 컬럼은 `0`으로 채워집니다.

---

## 6. 관련 문서

상세 설계 근거는 `docs/` 폴더를 참조하세요.

| 문서 | 내용 |
|---|---|
| `docs/constitution.md` | 개발 불변 원칙 (셀렉터 전략, 오류 격리 등) |
| `docs/spec.md` | 수집 데이터 명세 및 인수 기준 |
| `docs/plan.md` | 페이지별 파싱 전략 및 기술 구현 계획 |
| `docs/tasks.md` | 구현 작업 분해 체크리스트 |
