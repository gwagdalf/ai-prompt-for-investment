#!/usr/bin/env python3
"""서비스 계정 JSON 키로 Google Sheets API 호출."""

import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_service():
    """서비스 계정 키로 Sheets API 서비스 객체를 반환합니다."""
    key_path = os.environ.get(
        "GOOGLE_SERVICE_ACCOUNT_KEY",
        "service_account.json",
    )

    if not os.path.exists(key_path):
        print(f"Error: 서비스 계정 키 파일을 찾을 수 없습니다: {key_path}")
        print("Google Cloud Console에서 JSON 키를 다운로드하여 현재 디렉토리에 저장하세요.")
        sys.exit(1)

    creds = service_account.Credentials.from_service_account_file(
        key_path, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def read_sheet(spreadsheet_id: str, range_name: str = "Sheet1!A1:Z100") -> list:
    """시트 데이터를 읽습니다."""
    service = get_service()
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    return result.get("values", [])


def append_sheet(
    spreadsheet_id: str,
    range_name: str,
    values: list[list[str]],
) -> dict:
    """시트에 데이터를 추가합니다."""
    service = get_service()
    body = {"values": values}
    return (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )


if __name__ == "__main__":
    SPREADSHEET_ID = "1t-4bblYFpFKW1d_aFALmZ0F_gXGQdIaZd22KnbOvBGM"

    print("=== 시트 데이터 조회 ===")
    rows = read_sheet(SPREADSHEET_ID, "Sheet1!A1:Z50")
    if not rows:
        print("데이터가 없습니다.")
    else:
        for row in rows:
            print(row)
