# Refactoring Tasks

## 작업 목록

아래 작업을 순서대로 진행합니다. 이전 단계가 완료된 후 다음 단계로 진행하세요.

---

### Task 1: `sheet_utils.py` 생성

**공통 모듈을 새로 만듭니다.**

포함 내용:
- `EXCLUDE_SHEETS`
- `MAX_ROW_LIMIT`
- `SOURCE_SPREADSHEET_ID` (기존 `get-sheet-names.py`의 `SPREADSHEET_ID`)
- `DEST_SHEET_ID`
- `CLASSIFICATION_COLS`
- `get_sheets_service(credentials)` — `build("sheets", "v4", credentials)` 래퍼
- `get_all_sheet_data(spreadsheet_id, sheet_names, credentials)` — 배치 조회
- `trim_by_row_count(values)` — A2 셀 row_count 기준 자르기
- `print_auth_info(user_info)` — 인증 계정 정보 출력
- `create_sheet(spreadsheet_id, sheet_name, credentials)`
- `write_data(spreadsheet_id, sheet_name, all_rows, credentials)`
- `format_percentage_range(spreadsheet_id, sheet_name, credentials)` — 서식 적용

---

### Task 2: `drive_user_info.py` 수정

- `print_auth_info(user_info)` 함수를 `sheet_utils.py`로 이동하거나 별도 공통 함수로 제공
- 기존 `get_current_user()`는 그대로 유지

---

### Task 3: `get-sheet-details.py` 리팩토링

- `EXCLUDE_SHEETS`, `MAX_ROW_LIMIT` → `sheet_utils`에서 import
- `get_all_sheet_data()` → `sheet_utils`에서 import
- `row_count` 파싱 → `sheet_utils.trim_by_row_count()` 사용
- 불필요한 중복 코드 제거

---

### Task 4: `cp_sheet_details.py` 리팩토링

- `EXCLUDE_SHEETS`, `MAX_ROW_LIMIT`, `DEST_SHEET_ID`, `CLASSIFICATION_COLS` → `sheet_utils`에서 import
- `get_all_sheet_data()`, `create_sheet()`, `write_data()`, `format_percentage_range()` → `sheet_utils`에서 import
- `row_count` 파싱 → `sheet_utils.trim_by_row_count()` 사용
- 비즈니스 로직만 유지 (`build_header()`, `apply_classification()`, `is_header_row()`, `load_classification()`, 메인 루프)

---

### Task 5: `classification.py` 리팩토링

- `print_auth_info()` 공통 함수 사용 (선택)
- `CLASSIFICATION_COLS` → `sheet_utils`에서 import

---

### Task 6: `get-sheet-names.py` 리팩토링

- `SPREADSHEET_ID` → `sheet_utils.SOURCE_SPREADSHEET_ID` 사용
- `print_auth_info()` 공통 함수 사용 (선택)

---

### Task 7: 최종 검증

- 모든 스크립트 `import` 확인
- 각 스크립트 실행 테스트 (`python get-sheet-names.py`, `python get-sheet-details.py`, `python classification.py`, `python cp_sheet_details.py`)
- `refactoring-checks.md` 항목 체크
