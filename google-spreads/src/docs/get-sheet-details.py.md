# get-sheet-details.py

모든 시트의 상세 데이터를 가져와 콘솔에 출력하는 스크립트입니다.

## 개요

스프레드시드의 각 시트에서 `batchGet()` API로 한 번의 호출로 모든 시트 데이터를 가져옵니다. A2 셀에 저장된 `row_count` 값을 읽어 실제 데이터 행까지만 필터링합니다.

## 주요 기능

- **배치 조회**: `batchGet()`으로 여러 시트 데이터를 단일 API 호출로 가져옴
- **동적 행 필터링**: A2 셀의 `row_count` 값 기준으로 데이터 자르기
- **제외 시트**: `Weight`, `계좌리스트`, `Sum`, `z6키움비과세`, `z26방빵키움비과세`

## 주요 함수

### `get_all_sheet_data(spreadsheet_id, sheet_names, credentials)`

여러 시트의 데이터를 `batchGet()`으로 한 번에 가져옵니다.

- **파라미터**:
  - `spreadsheet_id`: 스프레드시트 ID
  - `sheet_names`: 시트 이름 목록
  - `credentials`: Google OAuth2 인증 정보
- **반환값**: `list` — `valueRanges` 결과 목록

## 의존성

- `drive_user_info.get_current_user`
- `get-sheet-names.py` (모듈 임포트)
