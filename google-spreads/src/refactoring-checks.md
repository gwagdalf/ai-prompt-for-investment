# Refactoring Checks

## 완료 체크리스트

각 항목이 완료되면 `[ ]` → `[x]`로 표시하세요.

---

### Task 1: `sheet_utils.py` 생성

- [ ] 파일 생성됨
- [ ] `EXCLUDE_SHEETS` 정의
- [ ] `MAX_ROW_LIMIT` 정의
- [ ] `SOURCE_SPREADSHEET_ID` 정의
- [ ] `DEST_SHEET_ID` 정의
- [ ] `CLASSIFICATION_COLS` 정의
- [ ] `get_sheets_service(credentials)` 함수 구현
- [ ] `get_all_sheet_data()` 함수 구현
- [ ] `trim_by_row_count(values)` 함수 구현
- [ ] `print_auth_info(user_info)` 함수 구현
- [ ] `create_sheet()` 함수 구현
- [ ] `write_data()` 함수 구현
- [ ] `format_percentage_range()` 함수 구현
- [ ] `python -c "from sheet_utils import ..."` import 테스트 성공

---

### Task 2: `drive_user_info.py` 수정

- [ ] 기존 `get_current_user()` 동작 확인
- [ ] 기존 사용자 확인 (`python drive_user_info.py`)
- [ ] 다른 스크립트들의 `from drive_user_info import get_current_user` still works

---

### Task 3: `get-sheet-details.py` 리팩토링

- [ ] `EXCLUDE_SHEETS`를 `sheet_utils`에서 import
- [ ] `MAX_ROW_LIMIT`를 `sheet_utils`에서 import
- [ ] `get_all_sheet_data()`를 `sheet_utils`에서 import
- [ ] `trim_by_row_count()`를 `sheet_utils`에서 사용
- [ ] 중복 함수/상수 제거됨
- [ ] `python get-sheet-details.py` 실행 성공
- [ ] 콘솔 출력이 기존과 동일

---

### Task 4: `cp_sheet_details.py` 리팩토링

- [ ] `EXCLUDE_SHEETS`를 `sheet_utils`에서 import
- [ ] `MAX_ROW_LIMIT`를 `sheet_utils`에서 import
- [ ] `DEST_SHEET_ID`를 `sheet_utils`에서 import
- [ ] `CLASSIFICATION_COLS`를 `sheet_utils`에서 import
- [ ] `get_all_sheet_data()`를 `sheet_utils`에서 import
- [ ] `create_sheet()`를 `sheet_utils`에서 import
- [ ] `write_data()`를 `sheet_utils`에서 import
- [ ] `format_percentage_range()`를 `sheet_utils`에서 import
- [ ] `trim_by_row_count()`를 `sheet_utils`에서 사용
- [ ] 중복 함수 제거됨
- [ ] 비즈니스 로직(`build_header`, `apply_classification`, `is_header_row`, `load_classification`, 메인 루프)만 남음
- [ ] `python cp_sheet_details.py` 실행 성공
- [ ] 대상 시트에 데이터 정상 저장
- [ ] 분류 수식 정상 적용
- [ ] 퍼센트 서식 정상 적용

---

### Task 5: `classification.py` 리팩토링

- [ ] `CLASSIFICATION_COLS`를 `sheet_utils`에서 import
- [ ] `python classification.py` 실행 성공
- [ ] `classification.csv` 정상 생성

---

### Task 6: `get-sheet-names.py` 리팩토링

- [ ] `SPREADSHEET_ID`를 `sheet_utils`에서 import
- [ ] `python get-sheet-names.py` 실행 성공
- [ ] 시트 목록 정상 출력

---

### Task 7: 최종 검증

- [ ] 모든 스크립트 `import` 에러 없음
- [ ] `get-sheet-names.py` → 정상 실행
- [ ] `get-sheet-details.py` → 정상 실행
- [ ] `classification.py` → 정상 실행
- [ ] `cp_sheet_details.py` → 정상 실행
- [ ] 불필요한 중복 코드 전무
- [ ] 코드 라인 수 감소 (이전 대비 최소 30% 감소)
