#!/usr/bin/env python3
"""get-sheet-details.py 데이터를 읽어 대상 스프레드시트에 복사합니다."""

import datetime
import importlib.util
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

_script_dir = os.path.dirname(os.path.abspath(__file__))
_gsn_path = os.path.join(_script_dir, "get-sheet-names.py")
_gsn_spec = importlib.util.spec_from_file_location("get_sheet_names", _gsn_path)
_gsn_mod = importlib.util.module_from_spec(_gsn_spec)
_gsn_spec.loader.exec_module(_gsn_mod)
get_sheet_names = _gsn_mod.get_sheet_names
SPREADSHEET_ID = _gsn_mod.SPREADSHEET_ID

from drive_user_info import get_current_user

EXCLUDE_SHEETS = {
    "Weight",
    "계좌리스트",
    "Sum",
    "z6키움비과세",
    "z26방빜키움비과세",
}

DEST_SHEET_ID = "1VqizBSVp7PqmWMFKW9rfzXpg629lenxjWzgwaP1mg3k"

HEADER = ["32", "접두", "코드", "code", "2026-04-24", "수량", "평균단가", "현재가", "수익률", "매입금액", "평가금액", "평가손익"]

MAX_ROW_LIMIT = 1000


def get_all_sheet_data(spreadsheet_id, sheet_names, credentials):
    service = build("sheets", "v4", credentials=credentials)
    ranges = [f"{name}!A2:L{MAX_ROW_LIMIT}" for name in sheet_names]
    result = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id, ranges=ranges
    ).execute()
    return result.get("valueRanges", [])


def create_sheet(spreadsheet_id, sheet_name, credentials):
    service = build("sheets", "v4", credentials=credentials)
    body = {"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]}
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body
    ).execute()
    print(f"새 시트 생성: {sheet_name}")


def write_data(spreadsheet_id, sheet_name, all_rows, credentials):
    service = build("sheets", "v4", credentials=credentials)
    body = {"values": all_rows}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()
    updated_rows = result.get("updatedRows", 0)
    updated_cols = result.get("updatedColumns", 0)
    print(f"데이터 저장 완료: {updated_rows}행, {updated_cols}열")


if __name__ == "__main__":
    user_info, credentials = get_current_user()
    user = user_info.get("user", {})
    display_name = user.get("displayName", "")
    email = user.get("emailAddress", "")
    print(f"인증 계정: {display_name} ({email})")
    print()

    all_sheet_names = get_sheet_names(SPREADSHEET_ID, credentials)
    target_sheets = [name for name in all_sheet_names if name not in EXCLUDE_SHEETS]
    print(f"전체 시트: {len(all_sheet_names)}개 / 처리 대상: {len(target_sheets)}개 (제외: {len(EXCLUDE_SHEETS)}개)")

    print("소스 시트 데이터 가져오는 중...")
    batch_results = get_all_sheet_data(SPREADSHEET_ID, target_sheets, credentials)

    all_rows = [HEADER]
    total_rows = 0
    for sheet_name, sheet_data in zip(target_sheets, batch_results):
        values = sheet_data.get("values", [])
        if not values:
            continue
        row_count = 0
        if values and values[0]:
            try:
                row_count = int(values[0][0])
            except ValueError:
                pass
        if row_count > 1 and row_count < len(values) + 1:
            values = values[: row_count - 1]
        all_rows.extend(values)
        total_rows += len(values)
        print(f"  [{sheet_name}] {len(values)}행")

    print(f"총 {total_rows}행 수집")

    now = datetime.datetime.now()
    new_sheet_name = now.strftime("%Y%m%d_%H%M%S")
    print(f"대상 시트: {DEST_SHEET_ID}")
    print(f"새 시트 이름: {new_sheet_name}")

    create_sheet(DEST_SHEET_ID, new_sheet_name, credentials)
    write_data(DEST_SHEET_ID, new_sheet_name, all_rows, credentials)
