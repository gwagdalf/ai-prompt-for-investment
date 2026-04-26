# get-sheet-names.py

Google Spreadsheet의 시트 이름 목록을 조회하는 스크립트입니다.

## 개요

지정된 스프레드시드의 모든 시트 이름을 가져옵니다. 다른 스크립트(`get-sheet-details.py`, `cp_sheet_details.py`)에서 모듈로 임포트하여 `get_sheet_names()` 함수와 `SPREADSHEET_ID` 상수를 재사용합니다.

## 주요 함수

### `get_sheet_names(spreadsheet_id, credentials)`

스프레드시트의 모든 시트 이름을 반환합니다.

- **파라미터**:
  - `spreadsheet_id`: 스프레드시트 ID
  - `credentials`: Google OAuth2 인증 정보
- **반환값**: `list[str]` — 시트 이름 목록

## 상수

- `SPREADSHEET_ID`: 기본 타겟 스프레드시트 ID (`1t-4bblYFpFKW1d_aFALmZ0F_gXGQdIaZd22KnbOvBGM`)

## 실행 방법

```bash
# 기본 스프레드시트
python get-sheet-names.py

# 다른 스프레드시트 지정
python get-sheet-names.py <SPREADSHEET_ID>
```

## 의존성

- `drive_user_info.get_current_user`
- `googleapiclient.discovery`
