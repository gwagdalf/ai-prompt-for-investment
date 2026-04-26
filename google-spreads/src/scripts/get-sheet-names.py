#!/usr/bin/env python3
"""Google Spreadsheet의 시트 이름 목록을 출력합니다."""

import sys
import os

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.auth import get_current_user, print_auth_info
from lib.sheets import SOURCE_SPREADSHEET_ID, get_sheets_service


def get_sheet_names(spreadsheet_id, credentials):
    """스프레드시트의 모든 시트 이름을 반환합니다."""
    service = get_sheets_service(credentials)
    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id, fields="sheets(properties/title)"
    ).execute()
    return [sheet["properties"]["title"] for sheet in result.get("sheets", [])]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        spreadsheet_id = sys.argv[1]
    else:
        spreadsheet_id = SOURCE_SPREADSHEET_ID

    user_info, credentials = get_current_user()
    print_auth_info(user_info)

    print(f"Spreadsheet ID: {spreadsheet_id}")
    print("=== 시트 목록 ===")

    sheet_names = get_sheet_names(spreadsheet_id, credentials)

    if not sheet_names:
        print("시트가 없습니다.")
    else:
        for i, name in enumerate(sheet_names, 1):
            print(f"  {i}. {name}")
