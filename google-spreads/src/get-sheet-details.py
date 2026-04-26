#!/usr/bin/env python3
"""모든 시트의 상세 데이터를 가져와 출력합니다.

- A2 셀에 저장된 row_count 값을 읽은 뒤
- A2 부터 L{row_count} 범위까지의 데이터를 가져옵니다.
- 제외 시트: Weight, 계좌리스트, Sum, z6키움비과세, z26방빵키움비과세방빜키움비과세
"""

import os
import sys
import importlib.util

from googleapiclient.discovery import build

from drive_user_info import get_current_user

# 하이픈이 있는 파일명 임포트
_script_dir = os.path.dirname(os.path.abspath(__file__))
_gsn_path = os.path.join(_script_dir, "get-sheet-names.py")
_gsn_spec = importlib.util.spec_from_file_location("get_sheet_names", _gsn_path)
_gsn_mod = importlib.util.module_from_spec(_gsn_spec)
_gsn_spec.loader.exec_module(_gsn_mod)
get_sheet_names = _gsn_mod.get_sheet_names
SPREADSHEET_ID = _gsn_mod.SPREADSHEET_ID

EXCLUDE_SHEETS = {
    "Weight",
    "계좌리스트",
    "Sum",
    "z6키움비과세",
    "z26방빵키움비과세방빵키움비과세",
}


def get_row_count(spreadsheet_id: str, sheet_name: str, credentials) -> int:
    """A2 셀에서 row_count 값을 읽습니다."""
    service = build("sheets", "v4", credentials=credentials)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A2")
        .execute()
    )
    values = result.get("values", [])
    if not values or not values[0]:
        return 0
    try:
        return int(values[0][0])
    except ValueError:
        return 0


def get_sheet_data(
    spreadsheet_id: str, sheet_name: str, row_count: int, credentials
) -> list:
    """A2 부터 L{row_count} 범위의 데이터를 가져옵니다."""
    service = build("sheets", "v4", credentials=credentials)
    range_name = f"{sheet_name}!A2:L{row_count}"
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    return result.get("values", [])


if __name__ == "__main__":
    # 인증: credentials를 한 번만 생성하여 재사용
    user_info, credentials = get_current_user()
    user = user_info.get("user", {})
    print(f"인증 계정: {user.get('displayName')} ({user.get('emailAddress')})")
    print(f"Spreadsheet ID: {SPREADSHEET_ID}")
    print()

    # 모든 시트 이름 가져오기
    all_sheet_names = get_sheet_names(SPREADSHEET_ID, credentials)
    target_sheets = [name for name in all_sheet_names if name not in EXCLUDE_SHEETS]

    print(f"전체 시트: {len(all_sheet_names)}개 / 처리 대상: {len(target_sheets)}개 (제외: {len(EXCLUDE_SHEETS)}개)")
    print()

    for sheet_name in target_sheets:
        row_count = get_row_count(SPREADSHEET_ID, sheet_name, credentials)
        if row_count < 2:
            print(f"--- [{sheet_name}] row_count={row_count} (데이터 없음) ---")
            print()
            continue

        data = get_sheet_data(SPREADSHEET_ID, sheet_name, row_count, credentials)
        print(f"--- [{sheet_name}] A2:L{row_count} ({len(data)} rows) ---")
        for row in data:
            print(row)
        print()
