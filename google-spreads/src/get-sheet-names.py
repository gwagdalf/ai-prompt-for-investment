#!/usr/bin/env python3
"""Google Spreadsheet의 시트 이름 목록을 출력합니다."""

import os
import sys

from googleapiclient.discovery import build

from drive_user_info import get_current_user

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_ID = "1t-4bblYFpFKW1d_aFALmZ0F_gXGQdIaZd22KnbOvBGM"


def get_sheet_names(spreadsheet_id: str, credentials) -> list[str]:
    """스프레드시트의 모든 시트 이름을 반환합니다."""
    service = build("sheets", "v4", credentials=credentials)

    result = (
        service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id, fields="sheets(properties/title)")
        .execute()
    )

    return [sheet["properties"]["title"] for sheet in result.get("sheets", [])]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        SPREADSHEET_ID = sys.argv[1]
    else:
        SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", SPREADSHEET_ID)

    # 인증: credentials를 한 번만 생성하여 재사용
    user_info, credentials = get_current_user()
    user = user_info.get("user", {})
    print(f"인증 계정: {user.get('displayName')} ({user.get('emailAddress')})")
    print()

    print(f"Spreadsheet ID: {SPREADSHEET_ID}")
    print("=== 시트 목록 ===")

    sheet_names = get_sheet_names(SPREADSHEET_ID, credentials)

    if not sheet_names:
        print("시트가 없습니다.")
    else:
        for i, name in enumerate(sheet_names, 1):
            print(f"  {i}. {name}")
