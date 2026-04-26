#!/usr/bin/env python3
"""모든 시트의 상세 데이터를 가져와 출력합니다.

- batchGet()으로 모든 시트 데이터를 한 번의 API 호출로 가져옵니다.
- A2 셀에서 row_count 값을 읽어 데이터를 필터링합니다.
- 제외 시트: Weight, 계좌리스트, Sum, z6키움비과세, z26방빜키움비과세
"""

import os
import sys
import codecs
import importlib.util

from googleapiclient.discovery import build

from drive_user_info import get_current_user

sys.stdout.reconfigure(encoding='utf-8')

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
    "z26방빵키움비과세",
}

# A2에서 읽어온 최대 행 수. 이 값보다 많으면 잘라서 처리합니다.
MAX_ROW_LIMIT = 1000


def get_all_sheet_data(
    spreadsheet_id: str, sheet_names: list[str], credentials
) -> list:
    """batchGet()으로 여러 시트 데이터를 한 번의 API 호출로 가져옵니다."""
    service = build("sheets", "v4", credentials=credentials)
    ranges = [f"{name}!A2:O{MAX_ROW_LIMIT}" for name in sheet_names]

    result = (
        service.spreadsheets()
        .values()
        .batchGet(spreadsheetId=spreadsheet_id, ranges=ranges)
        .execute()
    )
    return result.get("valueRanges", [])


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

    # 모든 시트 데이터를 한 번의 API 호출로 가져오기
    print("데이터 가져오는 중...")
    batch_results = get_all_sheet_data(SPREADSHEET_ID, target_sheets, credentials)

    for sheet_name, sheet_data in zip(target_sheets, batch_results):
        values = sheet_data.get("values", [])
        if not values:
            print(f"--- [{sheet_name}] 데이터 없음 ---")
            print()
            continue

        # A2 셀에서 row_count 읽기
        row_count = 0
        if values and values[0]:
            try:
                row_count = int(values[0][0])
            except ValueError:
                pass

        # row_count가 유효하면 해당 행까지만 잘라냄
        if row_count > 1 and row_count + 2 < len(values) - 1:
            values = values[: row_count + 1]  # -1: A2가 시작점이므로

        print(f"sheet명 : {sheet_name}")
        for row in values:
            row_with_name = [sheet_name] + row
            print(row_with_name)
        print()
