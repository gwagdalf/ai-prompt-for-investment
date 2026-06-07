# Spec — Yahoo Finance 재무 컨센서스 크롤러

> **상태:** Draft · **출처:** `crawl_yahoo.md` · **참고 구현:** `crawl_fnguide.py`
> 이 문서는 **무엇을(What) / 왜(Why)** 를 정의한다. 구현 방법(How)은 `plan.md` 참조.

---

## 1. 목적 (Why)

`finance.yahoo.com` 에서 미국 상장 종목들의 재무 컨센서스/추정치 데이터를 수집하여,
`crawl_fnguide.py` 와 호환되는 형식의 **단일 CSV** 로 저장한다.
다운스트림(투자 분석 시트)이 한국(FnGuide)·미국(Yahoo) 종목을 동일 스키마로 다룰 수 있게 한다.

## 2. 범위 (Scope)

### In scope
- 미리 정의된 미국 티커 목록(예: `AAPL`, `NVDA`)을 순차 처리.
- 종목당 5개 Yahoo 페이지에서 지표 수집.
- 종목 단위 오류 격리 + 단일 CSV 취합 저장.
- Selenium(탐색) + BeautifulSoup(파싱).

### Out of scope
- 실시간/스케줄링 자동화, DB 적재, 데이터 시각화.
- Yahoo 로그인/프리미엄 데이터.
- 한국 종목(이미 `crawl_fnguide.py` 가 담당).

## 3. 사용자 스토리

- **US-1:** 분석가로서 티커 리스트를 정의하고 스크립트를 1회 실행하면, 모든 종목의 컨센서스가 담긴 CSV 한 개를 얻고 싶다.
- **US-2:** 일부 종목 페이지가 깨져도 나머지 종목 데이터는 정상 수집되길 원한다.
- **US-3:** 결과 CSV가 FnGuide 출력과 같은 컬럼 규약을 따라 곧바로 병합 가능하길 원한다.

## 4. 수집 데이터 명세 (출처 페이지 기준)

> 모든 `{stock_code}` 는 티커(예: `AAPL`).

### 4.1 `financials` — `https://finance.yahoo.com/quote/{stock_code}/financials/`
| 결과 키 | 출처 | 비고 |
|---|---|---|
| `company` | `<h1>` 회사명 (예: `Apple Inc. (AAPL)` → `Apple Inc.`) | 괄호 앞부분만 |
| `Revenue(B)2024/12` | Total Revenue, 컬럼 `12/31/2024` | 십억 달러 단위 |
| `Revenue(B)2025/12` | Total Revenue, 컬럼 `12/31/2025` | 십억 달러 단위 |
| `eps2024/12` | `Basic EPS` 행, 컬럼 `12/31/2024` | |
| `eps2025/12` | `Basic EPS` 행, 컬럼 `12/31/2025` | |

### 4.2 `analysis` — `https://finance.yahoo.com/quote/{stock_code}/analysis/`
| 결과 키 | 출처 | 비고 |
|---|---|---|
| `Revenue(B)2026/12` | **Revenue Estimate** → `Avg. Estimate` → `Current Year (2026)` | `487.04B` 형태 파싱 |
| `Revenue(B)2027/12` | **Revenue Estimate** → `Avg. Estimate` → `Next Year (2027)` | |
| `eps2026/12` | **Earnings Estimate** → `Avg. Estimate` → `Current Year (2026)` | ⚠️ 원문 오타: `Revenue(B)` 로 적혀 있으나 EPS 가 맞음 |
| `eps2027/12` | **Earnings Estimate** → `Avg. Estimate` → `Next Year (2027)` | ⚠️ 동일 오타 |

### 4.3 `key-statistics` — `https://finance.yahoo.com/quote/{stock_code}/key-statistics/`
| 결과 키 | 출처 | 비고 |
|---|---|---|
| `bps2026/12` | `Price/Book` **Current** 값 | |
| `bps2025/12` | `Price/Book` 의 `12/31/2025, 9/30/2025, 6/30/2025, 3/31/2025` **4개 분기 평균** | |
| `dps2026/12` | `Forward Annual Dividend Rate` | ⚠️ 원문은 BPS 섹션에 기재되어 있으나 DPS 지표임 |

### 4.4 `history` (배당) — `https://finance.yahoo.com/quote/{stock_code}/history/?filter=div&frequency=1mo&period1={past_5y_ts}&period2={now_ts}`
| 결과 키 | 출처 | 비고 |
|---|---|---|
| `dps2025/12` | 2025년 ex-date 배당금 **합산** | |
| `dps2024/12` | 2024년 ex-date 배당금 **합산** | |

> ⚠️ 원문 URL 의 `period2={past_5y_timestamp}` 는 오타. 올바른 형식은 `period1=과거5년, period2=오늘` (원문 예시 URL이 정답).

### 4.5 `quote` (메인) — `https://finance.yahoo.com/quote/{stock_code}/`
| 결과 키 | 출처 | 비고 |
|---|---|---|
| `적정주가Min` | Analyst Price Targets **Low** | |
| `적정주가Max` | Analyst Price Targets **High** | |
| `적정주가Consensus` | Analyst Price Targets **Average** | |
| `beta` | `Beta (5Y Monthly)` | |

## 5. 출력 명세 (CSV)

- **인코딩:** `utf-8-sig`, `newline=''`, `csv.DictWriter`.
- **파일명:** `yahoo-{company}포함{N}개-{code}-{YYYYMMDD-HHMMSS}.csv`
  - ⚠️ 원문 `fnguide-` 접두사는 오타로 간주, `yahoo-` 사용 (clarification C-5 참조).
- **헤더(고정 순서):**
  ```
  code, company, beta,
  Revenue(B)2024/12, Revenue(B)2025/12, Revenue(B)2026/12, Revenue(B)2027/12,
  eps2024/12, eps2025/12, eps2026/12, eps2027/12,
  bps2025/12, bps2026/12,
  dps2024/12, dps2025/12, dps2026/12,
  적정주가Max, 적정주가Consensus, 적정주가Min
  ```

## 6. 비기능 요구사항

- **견고성:** 종목 단위 격리(Constitution Art.2), 견고한 셀렉터(Art.3).
- **이식성:** Windows + Chrome + `webdriver_manager` 자동 드라이버.
- **유지보수성:** 참고 구현과 동일 구조(Art.1).

## 7. 인수 기준 (Acceptance Criteria)

1. `STOCK_CODES` 의 모든 티커가 처리되고, 1개 실패해도 배치가 계속된다.
2. 정상 종목은 §5 헤더의 모든 컬럼에 합리적 값(또는 미수집 시 `0`)을 가진다.
3. 회사명에서 괄호/티커가 제거된다 (`Apple Inc.`).
4. Revenue 가 십억 달러(B) 단위로 저장된다.
5. CSV 가 §5 파일명 규약으로 생성되고 Excel 에서 한글 깨짐 없이 열린다.
6. 실행 중 종목별 진행 로그가 출력된다.

## 8. 미해결 사항 / Clarifications

| ID | 항목 | 가정한 처리 |
|---|---|---|
| C-1 | 문서 제목/내용의 "FnGuide" 표기 | Yahoo 크롤러로 해석 |
| C-2 | EPS 섹션의 "revenue" 표기(L78) | `eps2025/12` 로 해석 |
| C-3 | Earnings Estimate → `Revenue(B)` 저장 표기(L119-120) | `eps2026/12`, `eps2027/12` 로 해석 |
| C-4 | `Forward Annual Dividend Rate` 가 BPS 섹션에 위치 | `dps2026/12` DPS 지표로 해석 |
| C-5 | 파일명 `fnguide-` 접두사 | `yahoo-` 로 변경 |
| C-6 | history URL 의 `period2` 오타 | `period2 = now_ts` 로 수정 |
| C-7 | analysis 페이지 "Annual" 토글 필요 여부 | Estimate 테이블은 Current/Next Year 컬럼이 이미 연 단위 → 토글 없이 파싱 가능. 차트 토글은 무시 |
| C-8 | 쿠키/동의 배너 처리 | 등장 시 수락 시도, 실패해도 진행 |
