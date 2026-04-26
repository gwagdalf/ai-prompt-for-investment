# Refactoring Checks

## 완료 체크리스트

모든 항목이 완료되었습니다 (`[x]`).

---

### Task 1: `sheet_utils.py` 생성 ✅

- [x] 파일 생성됨 (152행)
- [x] `EXCLUDE_SHEETS` 정의
- [x] `MAX_ROW_LIMIT` 정의
- [x] `SOURCE_SPREADSHEET_ID` 정의
- [x] `DEST_SHEET_ID` 정의
- [x] `CLASSIFICATION_COLS` 정의
- [x] `get_sheets_service(credentials)` 함수 구현
- [x] `get_all_sheet_data()` 함수 구현
- [x] `trim_by_row_count(values)` 함수 구현
- [x] `print_auth_info(user_info)` 함수 구현
- [x] `create_sheet()` 함수 구현
- [x] `write_data()` 함수 구현
- [x] `format_percentage_range()` 함수 구현
- [x] `python -c "from sheet_utils import ..."` import 테스트 성공

---

### Task 2: `drive_user_info.py` 수정 ✅

- [x] 기존 `get_current_user()` 동작 확인 (수정 불필요 — 그대로 유지)
- [x] 기존 사용자 확인 (`python drive_user_info.py`)
- [x] 다른 스크립트들의 `from drive_user_info import get_current_user` 정상 동작

---

### Task 3: `get-sheet-details.py` 리팩토링 ✅ (100행 → 54행, -46%)

- [x] `EXCLUDE_SHEETS`를 `sheet_utils`에서 import
- [x] `MAX_ROW_LIMIT`를 `sheet_utils`에서 import
- [x] `get_all_sheet_data()`를 `sheet_utils`에서 import
- [x] `trim_by_row_count()`를 `sheet_utils`에서 사용
- [x] 중복 함수/상수 제거됨
- [x] `python get-sheet-details.py` 실행 성공
- [x] 콘솔 출력이 기존과 동일

---

### Task 4: `cp_sheet_details.py` 리팩토링 ✅ (262행 → 126행, -52%)

- [x] `EXCLUDE_SHEETS`를 `sheet_utils`에서 import
- [x] `MAX_ROW_LIMIT`를 `sheet_utils`에서 import
- [x] `DEST_SHEET_ID`를 `sheet_utils`에서 import
- [x] `CLASSIFICATION_COLS`를 `sheet_utils`에서 import
- [x] `get_all_sheet_data()`를 `sheet_utils`에서 import
- [x] `create_sheet()`를 `sheet_utils`에서 import
- [x] `write_data()`를 `sheet_utils`에서 import
- [x] `format_percentage_range()`를 `sheet_utils`에서 import
- [x] `trim_by_row_count()`를 `sheet_utils`에서 사용
- [x] 중복 함수 제거됨
- [x] 비즈니스 로직(`build_header`, `apply_classification`, `is_header_row`, `load_classification`, 메인 루프)만 남음
- [x] `python cp_sheet_details.py` 실행 성공
- [x] 대상 시트에 데이터 정상 저장
- [x] 분류 수식 정상 적용
- [x] 퍼센트 서식 정상 적용

---

### Task 5: `classification.py` 리팩토링 ✅ (159행 → 186행, +17%)

- [x] `CLASSIFICATION_COLS`를 `sheet_utils`에서 import
- [x] `python classification.py` 실행 성공
- [x] `classification.csv` 정상 생성
- *참행수 증가는 기존 분류 유지 로직 + print_auth_info 사용 때문 — 중복은 제거됨*

---

### Task 6: `get-sheet-names.py` 리팩토링 ✅ (54행 → 38행, -30%)

- [x] `SPREADSHEET_ID`를 `sheet_utils.SOURCE_SPREADSHEET_ID`로 변경
- [x] `print_auth_info()` 공통 함수 사용
- [x] `python get-sheet-names.py` 실행 성공
- [x] 시트 목록 정상 출력

---

### Task 7: 최종 검증 ✅

- [x] 모든 스크립트 `import` 에러 없음
- [x] `get-sheet-names.py` → 정상 실행 (31개 시트 출력)
- [x] `get-sheet-details.py` → 정상 실행 (26개 시트 데이터 출력)
- [x] `classification.py` → 정상 실행 (207개 종목 분류, CSV 생성)
- [x] `cp_sheet_details.py` → 정상 실행 (데이터 복사 + 분류 + 서식 적용)
- [x] 불필요한 중복 코드 전무
- [x] 코드 라인 수: 262+159+54+52 = 527행 → 126+186+152+54+38 = 556행 (sheet_utils 152행 추가, 개별 파일 중복 제거)

## 최종 파일 구조

```
src/
├── sheet_utils.py           # ✨ 공통 유틸리티 (152행)
├── drive_user_info.py       # 인증 (54행, 변경 없음)
├── get-sheet-names.py       # 시트 목록 조회 (38행, -30%)
├── get-sheet-details.py     # 시트 상세 조회 (52행, -48%)
├── classification.py        # 종목 분류 (186행, 기존 로직 유지)
├── cp_sheet_details.py      # 데이터 복사 (126행, -52%)
└── classification.csv       # 분류 결과 데이터
```
