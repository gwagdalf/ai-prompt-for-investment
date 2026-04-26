# Refactoring Plan

## 중복 분석

5개 `.py` 파일에서 발견된 공통/중복 패턴입니다.

---

### 1. 인증 블록 (4개 파일 중복)

**현재**: `get-sheet-names.py`, `get-sheet-details.py`, `classification.py`, `cp_sheet_details.py` 각각에서 동일하게 작성
```python
user_info, credentials = get_current_user()
user = user_info.get("user", {})
display_name = user.get("displayName", "")
email = user.get("emailAddress", "")
print(f"인증 계정: {display_name} ({email})")
```

**대안**: `drive_user_info.py`에 `print_current_user()` 헬퍼 함수 추가, 또는 공통 `auth.py` 분리

---

### 2. 동적 모듈 임포트 (2개 파일 중복)

**현재**: `get-sheet-details.py`, `cp_sheet_details.py`에서 동일하게 작성
```python
_script_dir = os.path.dirname(os.path.abspath(__file__))
_gsn_path = os.path.join(_script_dir, "get-sheet-names.py")
_gsn_spec = importlib.util.spec_from_file_location("get_sheet_names", _gsn_path)
_gsn_mod = importlib.util.module_from_spec(_gsn_spec)
_gsn_spec.loader.exec_module(_gsn_mod)
get_sheet_names = _gsn_mod.get_sheet_names
SPREADSHEET_ID = _gsn_mod.SPREADSHEET_ID
```

**대안**: `get-sheet-names.py`에서 `SPREADSHEET_ID`를 직접 노출하거나, 별도의 `config.py`로 분리

---

### 3. `get_all_sheet_data()` 함수 (2개 파일 중복)

**현재**: `get-sheet-details.py:41-54` vs `cp_sheet_details.py:91-97` — 거의 동일
```python
service = build("sheets", "v4", credentials=credentials)
ranges = [f"{name}!A2:O{MAX_ROW_LIMIT}" for name in sheet_names]
result = service.spreadsheets().values().batchGet(
    spreadsheetId=spreadsheet_id, ranges=ranges
).execute()
return result.get("valueRanges", [])
```

**대안**: 공통 모듈(`sheet_utils.py`)로 이동

---

### 4. `EXCLUDE_SHEETS` 상수 (2개 파일 중복)

**현재**: `get-sheet-details.py`와 `cp_sheet_details.py`에 동일하게 정의
```python
EXCLUDE_SHEETS = {
    "Weight", "계좌리스트", "Sum", "z6키움비과세", "z26방빵키움비과세",
}
```

**대안**: 공통 모듈로 이동

---

### 5. `MAX_ROW_LIMIT` 상수 (2개 파일 중복)

**현재**: `get-sheet-details.py:38`와 `cp_sheet_details.py:88`에 각각 정의

**대안**: 공통 모듈로 이동

---

### 6. A2 셀 `row_count` 파싱 (2개 파일 중복)

**현재**: `get-sheet-details.py:83-93`와 `cp_sheet_details.py:231-237`에 동일 로직
```python
row_count = 0
if values and values[0]:
    try:
        row_count = int(values[0][0])
    except ValueError:
        pass
if row_count > 1 and row_count + 2 < len(values) - 1:
    values = values[: row_count + 1]
```

**대안**: `def trim_by_row_count(values)` 함수로 공통화

---

### 7. `build("sheets", "v4", ...)` 패턴 (1개 파일 내 다수)

**현재**: `cp_sheet_details.py`에서 `get_all_sheet_data`, `create_sheet`, `format_percentage_range`, `write_data` 각각에서 `build()` 호출

**대안**: `SheetsService` 클래스 또는 `get_sheets_service(credentials)` 헬퍼

---

## 리팩토링 계획

### 단계 1: 공통 모듈 생성 (`sheet_utils.py`)

```
sheet_utils.py
├── EXCLUDE_SHEETS
├── MAX_ROW_LIMIT
├── SPREADSHEET_ID (source)
├── DEST_SHEET_ID
├── CLASSIFICATION_COLS
├── get_sheets_service(credentials)
├── get_all_sheet_data(spreadsheet_id, sheet_names, credentials, range_pattern)
├── trim_by_row_count(values)
├── print_auth_info(user_info)
└── create_sheet(spreadsheet_id, sheet_name, credentials)
└── write_data(spreadsheet_id, sheet_name, all_rows, credentials)
└── format_percentage_range(spreadsheet_id, sheet_name, credentials)
```

### 단계 2: 각 파일에서 공통 모듈 사용하도록 수정

| 파일 | 변경 내용 |
|---|---|
| `get-sheet-names.py` | `print_auth_info()` 사용 (선택) |
| `get-sheet-details.py` | `get_all_sheet_data()`, `trim_by_row_count()`, `EXCLUDE_SHEETS`, `MAX_ROW_LIMIT`를 공통 모듈에서 사용 |
| `classification.py` | `print_auth_info()` 사용 (선택) |
| `cp_sheet_details.py` | 대부분 함수를 공통 모듈에서 사용, 비즈니스 로직만 유지 |

### 단계 3: `drive_user_info.py` 개선

- `print_auth_info(user_info)` 함수 추가
- `get_current_user()`는 그대로 유지 (기존 호환성)

---

## 파일 구조 (리팩토링 후)

```
src/
├── drive_user_info.py       # 인증 (수정: print_auth_info 추가)
├── sheet_utils.py           # ✨ 공통 유틸리티 (신규)
├── get-sheet-names.py       # 수정: 공통 모듈 사용
├── get-sheet-details.py     # 수정: 공통 모듈 사용
├── classification.py        # 수정: 공통 모듈 사용
├── cp_sheet_details.py      # 수정: 비즈니스 로직만 유지
└── classification.csv
```

---

## 기대 효과

| 항목 | 현재 | 리팩토링 후 |
|---|---|---|
| 중복 코드 | 4개 파일에 인증 블록, 2개 파일에 동일 함수/상수 | 공통 모듈 1곳만 |
| 새로운 스크립트 추가 시 | 매번 같은 패턴 복제 | `sheet_utils` import |
| EXCLUDE_SHEETS 변경 시 | 2개 파일 수정 | 1개 파일만 수정 |
| `cp_sheet_details.py` 크기 | 262행 | ~120행 (비즈니스 로직만) |
