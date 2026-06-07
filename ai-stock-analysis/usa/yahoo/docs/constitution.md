# Constitution — Yahoo Finance 재무 크롤러 (`crawl_yahoo.py`)

이 문서는 `crawl_yahoo.py` 개발 전반에 적용되는 **불변 원칙(governing principles)** 을 정의한다.
spec / plan / tasks 문서는 이 원칙과 충돌해서는 안 되며, 충돌 시 본 문서가 우선한다.

---

## Article 1. 기존 자산 재사용 (Consistency with Reference)

- 신규 스크립트는 동일 디렉터리의 `crawl_fnguide.py` 와 **동일한 코드 구조·함수 시그니처·네이밍 컨벤션**을 따른다.
  - `setup_driver()`, `parse_value()`, `get_stock_data(stock_code)`, `save_to_csv(data_list)`, `if __name__ == "__main__":`
- 결과 딕셔너리 키 네이밍, CSV 저장 방식(`utf-8-sig`, `DictWriter`), 파일명 생성 패턴을 그대로 계승한다.
- **이유:** 두 크롤러의 출력이 동일 다운스트림(분석/시트)에서 호환되어야 한다.

## Article 2. 종목 단위 격리 (Per-Stock Resilience)

- 한 종목의 실패가 **전체 배치를 중단시켜서는 안 된다.**
- 모든 스크래핑 로직은 `try...except Exception` 으로 감싸고, 실패 시 결과 딕셔너리를 기본값(`0` 또는 `'Error'`)으로 채워 반환한다.
- WebDriver 는 `try...finally` 의 `finally` 에서 **반드시 `driver.quit()`** 한다 (리소스 누수 금지).

## Article 3. 견고한 선택자 (Robust Selectors)

- Yahoo 의 해시 접미사 CSS 클래스(`yf-1duawpp`, `yf-1hgjbtd` 등)는 **배포마다 변한다.**
- 따라서 클래스명 단독 셀렉터를 금지한다. 우선순위:
  1. `data-testid` / `data-testid-header` / `data-testid-cell` 같은 안정 속성
  2. 행/항목의 **텍스트 라벨**(예: `"Basic EPS"`, `"Price/Book"`, `"Avg. Estimate"`)
  3. 의미 기반 구조(테이블 헤더의 연도 매칭)
- **이유:** 클래스 의존 셀렉터는 다음 주에 깨진다.

## Article 4. 데이터 정합성 (Data Integrity)

- 숫자 변환은 단일 함수 `parse_value()` 를 통한다. 단위 접미사(`B`, `M`, `%`), 콤마, 통화 기호, 공백을 일관되게 처리한다.
- 값을 찾지 못하면 추측하지 않는다 — `0` 으로 둔다.
- 단위 규약을 문서와 코드에서 일치시킨다 (Revenue 는 **십억 달러(B)** 단위로 저장).

## Article 5. 결정적 출력 (Deterministic Output)

- CSV 헤더(컬럼 순서)는 **고정**이며 모든 종목 행에 동일하게 적용된다.
- 실제로 수집 가능한 필드만 헤더에 포함한다 (수집하지 않는 연도 컬럼을 만들지 않는다).

## Article 6. 관측 가능성 (Observability)

- 각 종목 처리 시작/완료, 각 페이지 이동, 실패 사유를 `print` 로 남긴다.
- 사용자가 진행 상황과 실패 종목을 콘솔에서 식별할 수 있어야 한다.

## Article 7. 예의 바른 크롤링 (Responsible Scraping)

- 페이지 로드 후 명시적/암묵적 대기(`time.sleep` 또는 `WebDriverWait`)를 둔다.
- 헤드리스 모드를 기본으로 하되, 쿠키 동의 배너 등 차단 요소 처리 로직을 고려한다.
- 과도한 동시 요청을 하지 않는다 (순차 처리).

---

## 개정 (Amendment)

원칙 변경은 본 문서 수정 후 spec/plan/tasks 에 반영한다. 코드가 원칙과 어긋나면 코드가 아니라 원칙이 먼저다.
