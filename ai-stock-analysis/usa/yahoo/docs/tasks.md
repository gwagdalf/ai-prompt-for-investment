# Tasks — `crawl_yahoo.py` 구현 작업 분해

> 순서대로 실행. 각 작업은 `plan.md` 의 해당 섹션을 구현하고 `checklist.md` 항목으로 검증한다.
> 표기: `[ ]` 미완 · `[x]` 완료.

---

## Phase 0 — 준비
- [ ] **T0.1** `crawl_fnguide.py` 구조/함수 시그니처 재확인 (Art.1 일관성)
- [ ] **T0.2** 환경 확인: `selenium`, `webdriver_manager`, `bs4`, Chrome 설치 여부
- [ ] **T0.3** 검증용 샘플 티커 1개 선정(예: `AAPL`) — 개발 중 빠른 반복용

## Phase 1 — 스캐폴딩
- [ ] **T1.1** import 블록 작성 (`plan.md` §2, `timedelta` 포함)
- [ ] **T1.2** `setup_driver()` 작성/이식 (FnGuide 재사용)
- [ ] **T1.3** `parse_value()` Yahoo 확장: `B`/`M`/`%`/통화/콤마/`N/A`·`-` 처리
- [ ] **T1.4** (권장) `parse_revenue_b()` 단위 환산 헬퍼 분리
- [ ] **T1.5** `get_stock_data(stock_code)` 골격: `results={"code":...}`, `try/except/finally`, `driver.quit()`

## Phase 2 — 페이지별 수집 (각각 개별 try/except)
- [ ] **T2.1** `financials` 페이지 이동 + 회사명 추출(괄호 앞부분) → `company`
- [ ] **T2.2** `financials`: thead 날짜 헤더 동적 인덱싱
- [ ] **T2.3** `financials`: `Total Revenue` → `Revenue(B)2024/12`, `Revenue(B)2025/12` (십억 환산)
- [ ] **T2.4** `financials`: `Basic EPS` → `eps2024/12`, `eps2025/12`
- [ ] **T2.5** `analysis`: `Revenue Estimate` `Avg. Estimate` → `Revenue(B)2026/12`, `Revenue(B)2027/12`
- [ ] **T2.6** `analysis`: `Earnings Estimate` `Avg. Estimate` → `eps2026/12`, `eps2027/12` (C-3 오타 반영)
- [ ] **T2.7** `key-statistics`: `Price/Book` Current → `bps2026/12`
- [ ] **T2.8** `key-statistics`: `Price/Book` 최근 4분기 평균 → `bps2025/12` (헤더 날짜 매칭)
- [ ] **T2.9** `key-statistics`: `Forward Annual Dividend Rate` → `dps2026/12` (C-4)
- [ ] **T2.10** `history`: `past_5y_ts`/`now_ts` 계산 + 배당 URL 구성 (C-6 수정)
- [ ] **T2.11** `history`: 날짜→연도 파싱 후 연도별 합산 → `dps2024/12`, `dps2025/12`
- [ ] **T2.12** `quote`: Analyst Price Targets Low/High/Average → `적정주가Min`/`Max`/`Consensus`
- [ ] **T2.13** `quote`: `Beta (5Y Monthly)` (`title` 속성) → `beta`

## Phase 3 — 견고성
- [ ] **T3.1** 종료 전 `results.setdefault(key, 0)` 로 전체 헤더 키 보장
- [ ] **T3.2** 예외 시 `company` 기본값 `'Error'`, 진행 로그/실패 사유 `print`
- [ ] **T3.3** 페이지 간 대기(`sleep`/`WebDriverWait`) + (선택) 쿠키 배너 처리

## Phase 4 — 출력
- [ ] **T4.1** `save_to_csv(data_list)`: 빈 리스트 가드
- [ ] **T4.2** 파일명 `yahoo-{company}포함{N}개-{code}-{ts}.csv` (C-5)
- [ ] **T4.3** spec §5 고정 헤더 + `utf-8-sig` + `DictWriter`

## Phase 5 — 메인 & 검증
- [ ] **T5.1** `__main__`: 미국 `STOCK_CODES` + 루프 + 진행 로그 + 저장
- [ ] **T5.2** 단일 티커(`AAPL`) 스모크 테스트 — 값 합리성 육안 확인
- [ ] **T5.3** 2~3개 티커 배치 테스트 — 부분 실패 격리 동작 확인
- [ ] **T5.4** `checklist.md` 전 항목 통과 확인
