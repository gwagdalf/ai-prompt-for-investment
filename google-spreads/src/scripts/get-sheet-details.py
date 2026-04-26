#!/usr/bin/env python3
"""모든 시트의 상세 데이터를 가져와 출력합니다."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.auth import get_current_user, print_auth_info
from lib.sheets import SOURCE_SPREADSHEET_ID, EXCLUDE_SHEETS, get_all_sheet_data, trim_by_row_count

# get-sheet-names.py에서 get_sheet_names 함수 임포트
import importlib.util
_gsn_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "get-sheet-names.py")
_gsn_spec = importlib.util.spec_from_file_location("get_sheet_names", _gsn_path)
_gsn_mod = importlib.util.module_from_spec(_gsn_spec)
_gsn_spec.loader.exec_module(_gsn_mod)
get_sheet_names = _gsn_mod.get_sheet_names


if __name__ == "__main__":
    user_info, credentials = get_current_user()
    print_auth_info(user_info)
    print(f"Spreadsheet ID: {SOURCE_SPREADSHEET_ID}")

    all_sheet_names = get_sheet_names(SOURCE_SPREADSHEET_ID, credentials)
    target_sheets = [name for name in all_sheet_names if name not in EXCLUDE_SHEETS]
    print(f"전체 시트: {len(all_sheet_names)}개 / 처리 대상: {len(target_sheets)}개 (제외: {len(EXCLUDE_SHEETS)}개)")
    print()

    print("데이터 가져오는 중...")
    batch_results = get_all_sheet_data(SOURCE_SPREADSHEET_ID, target_sheets, credentials)

    for sheet_name, sheet_data in zip(target_sheets, batch_results):
        values = sheet_data.get("values", [])
        if not values:
            print(f"--- [{sheet_name}] 데이터 없음 ---")
            print()
            continue

        values = trim_by_row_count(values)

        print(f"sheet명 : {sheet_name}")
        for row in values:
            row_with_name = [sheet_name] + row
            print(row_with_name)
        print()
