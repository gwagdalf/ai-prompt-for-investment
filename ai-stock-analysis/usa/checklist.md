# Checklist — `crawl_yahoo.py` 완료 검증

> 모든 항목 `[x]` 가 되어야 인수(Acceptance) 완료. 출처: `spec.md` §7, `constitution.md`.

---

## A. 구조 / 일관성 (Constitution Art.1)
- [ ] `setup_driver`, `parse_value`, `get_stock_data`, `save_to_csv`, `__main__` 5요소 존재
- [ ] 함수 시그니처가 `crawl_fnguide.py` 와 호환
- [ ] 결과 딕셔너리 키 네이밍이 spec §5 헤더와 정확히 일치

## B. 데이터 정확성
- [ ] `company` 에서 ` (TICKER)` 제거됨 (예: `Apple Inc.`)
- [ ] `Revenue(B)2024/12`, `2025/12` 가 financials 에서 십억 단위로 수집
- [ ] `Revenue(B)2026/12`, `2027/12` 가 analysis Revenue Estimate `Avg.` 에서 수집
- [ ] `eps2024/12`, `2025/12` 가 financials `Basic EPS` 에서 수집
- [ ] `eps2026/12`, `2027/12` 가 analysis Earnings Estimate `Avg.` 에서 수집 (C-3)
- [ ] `bps2026/12` = Price/Book Current
- [ ] `bps2025/12` = Price/Book 최근 4분기 평균(헤더 날짜로 매칭)
- [ ] `dps2026/12` = Forward Annual Dividend Rate (C-4)
- [ ] `dps2025/12`, `dps2024/12` = 해당 연도 배당 합산(날짜→연도 파싱)
- [ ] `적정주가Min/Max/Consensus` = Analyst Price Targets Low/High/Average
- [ ] `beta` = Beta (5Y Monthly)

## C. 견고성 (Art.2, Art.3)
- [ ] 셀렉터가 해시 클래스(`yf-...`) 단독에 의존하지 않음 (텍스트/`data-testid` 사용)
- [ ] 컬럼 인덱스를 헤더 날짜로 동적 결정(고정 인덱스 미사용)
- [ ] 페이지별 `try/except` 로 부분 실패 격리
- [ ] `finally` 에서 `driver.quit()` 보장
- [ ] 1개 종목 실패해도 배치 계속 (`Error` 채움)
- [ ] 종료 전 모든 헤더 키 `setdefault(key, 0)`

## D. 출력 (spec §5)
- [ ] 파일명 패턴 `yahoo-{company}포함{N}개-{code}-{YYYYMMDD-HHMMSS}.csv` (C-5)
- [ ] 인코딩 `utf-8-sig`, `newline=''`, `DictWriter`
- [ ] 헤더 컬럼/순서가 spec §5 와 동일
- [ ] Excel 에서 한글 컬럼명 깨지지 않음

## E. 단위 / 정합성 (Art.4)
- [ ] `B`/`M`/`%`/콤마/통화기호/`N/A`·`-` 가 `parse_value` 에서 일관 처리
- [ ] Revenue 단위가 모든 연도(2024~2027)에서 동일(B) — 혼용 없음
- [ ] 미수집 값은 추측 없이 `0`

## F. 관측성 / 동작 (Art.6)
- [ ] 종목 시작/완료 + 페이지 이동 + 실패 사유 로그 출력
- [ ] 단일 티커(`AAPL`) 스모크 테스트 통과 (값 육안 합리성)
- [ ] 다중 티커 배치 테스트 통과 (부분 실패 격리 확인)

## G. Clarifications 반영 (spec §8)
- [ ] C-1~C-7 모두 spec 의 가정대로 코드에 반영
- [ ] 코드에 남은 추가 가정은 주석으로 명시
