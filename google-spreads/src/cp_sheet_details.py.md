# cp_sheet_details.py

소스 스프레드시트의 모든 시트 데이터를 읽어 대상 스프레드시트에 복사하는 스크립트입니다. 종목 분류(반도체/빅테크/Fintech/미국/한국/중국/World)와 퍼센트 서식 적용까지 수행합니다.

## 개요

여러 시트의 포트폴리오 데이터를 수집하여 하나의 통합 시트로 병합합니다. `classification.csv`를 로드하여 종목별 분류 수식을 적용하고, 대상 시트의 컬럼에 퍼센트 서식을 자동으로 설정합니다.

## 주요 기능

### 헤더 (2줄)

- **1행**: 날짜 기반 컬럼 + SUM 수식 (P~W)
- **2행**: `종목명`, `원평가` 포함 레이블 + 7개 분류 컬럼

### 데이터 처리

- **헤더성 행 필터**: `row[1] == "접두"`인 행은 모두 제거
- **종목 분류**: `classification.csv`에서 `row[3]`(코드)로 매칭하여 `=($P{row}/$P$1)` 수식 적용
- **중복 제거**: 소스 시트 내에서 분류된 헤더 행은 1회만 유지

### 서식 적용

- **P1**: `#,##0` 숫자 서식 (소수점 없음, 천단위 콤마)
- **Q1:W500**: `0%` 퍼센트 서식 (소수점 없음)

## 주요 함수

### `build_header()`

오늘 날짜를 포함한 2줄 헤더를 생성합니다.

### `load_classification()`

`classification.csv`를 읽어 `(코드) → {분류값}` 매핑을 반환합니다.

### `apply_classification(row, classification, row_num)`

소스 행에 종목 분류 수식을 추가합니다. 소스 row(16개 컬럼) + 분류 컬럼 7개 = 23개로 맞춥니다.

### `format_percentage_range(spreadsheet_id, sheet_name, credentials)`

Q:W 컬럼에 퍼센트 서식, P1에 숫자 서식을 적용합니다.

### `create_sheet(spreadsheet_id, sheet_name, credentials)`

대상 스프레드시트에 새 시트를 생성합니다.

### `write_data(spreadsheet_id, sheet_name, all_rows, credentials)`

데이터를 대상 시트에 쓰기(`update`)합니다.

## 실행 방법

```bash
python cp_sheet_details.py
```

## 출력

- 대상 스프레드시트(`1VqizBSVp7PqmWMFKW9rfzXpg629lenxjWzgwaP1mg3k`)에 `YYYYMMDD_HHMMSS` 이름의 새 시트 생성

## 제외 시트

`Weight`, `계좌리스트`, `Sum`, `z6키움비과세`, `z26방빵키움비과세`

## 의존성

- `drive_user_info.get_current_user`
- `get-sheet-names.py` (모듈 임포트)
- `classification.csv` (분류 데이터)
