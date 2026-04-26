#!/usr/bin/env python3
"""서비스 계정 JSON 키로 Google Sheets API 호출."""

import json
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_credentials():
    """서비스 계정 JSON 키에서 credentials를 생성합니다."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_key_path = os.path.join(base_dir, "..", "..", "..", "google-service-account.json")

    key_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY", default_key_path)

    if not os.path.exists(key_path):
        print(f"Error: 서비스 계정 키 파일을 찾을 수 없습니다: {key_path}")
        sys.exit(1)

    return service_account.Credentials.from_service_account_file(
        key_path, scopes=SCOPES
    )


def read_sheet(spreadsheet_id: str, range_name: str = "Sheet1!A1:Z100") -> list:
    """시트 데이터를 읽습니다."""
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

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
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

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
    rows = read_sheet(SPREADSHEET_ID, "Sum!A1:AE13")
    if not rows:
        print("데이터가 없습니다.")
    else:
        for row in rows:
            print(row)

    # --- 데이터 추가 ---
    # print("\n=== 시트에 데이터 추가 ===")
    # append_result = append_sheet(
    #     SPREADSHEET_ID,
    #     "Sheet1!A1",
    #     [["2026-04-26", "테스트", "100"]],
    # )
    # print(append_result)
