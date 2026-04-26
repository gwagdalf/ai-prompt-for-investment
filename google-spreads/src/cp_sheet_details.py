#!/usr/bin/env python3
"""get-sheet-details.py 데이터를 읽어 대상 스프레드시트에 복사합니다."""

import csv
import datetime
import importlib.util
import os
import sys
import codecs

from google.oauth2 import service_account
from googleapiclient.discovery import build

from drive_user_info import get_current_user

sys.stdout.reconfigure(encoding='utf-8')

# get-sheet-names.py에서 SPREADSHEET_ID 임포트
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

DEST_SHEET_ID = "1VqizBSVp7PqmWMFKW9rfzXpg629lenxjWzgwaP1mg3k"

def build_header():
    """오늘 날짜를 포함한 동적 헤더를 생성합니다."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    return ["계좌", "#", "접두", "코드", "code", today, "수량", "평균단가", "현재가", "수익률", "매입금액", "평가금액", "평가손익", "통화", "환율", "=SUM(P2:P500)","반도체","빅테크","미국","한국","중국","World"]

CLASSIFICATION_CSV = os.path.join(_script_dir, "classification.csv")
CLASSIFICATION_COLS = ["반도체", "빅테크", "미국", "한국", "중국", "World"]


def load_classification():
    """classification.csv를 로드하여 (코드, 종목명) → 분류값 매핑을 반환합니다."""
    lookup = {}
    try:
        with open(CLASSIFICATION_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row.get("코드", "").strip().lower()
                lookup[key] = {col: row.get(col, "0") for col in CLASSIFICATION_COLS}
    except FileNotFoundError:
        print(f"경고: {CLASSIFICATION_CSV} 파일을 찾을 수 없습니다.")
    return lookup


def apply_classification(row, classification):
    """row[2](코드)와 row[4](종목명)로 분류 데이터를 매핑하여 컬럼을 추가합니다."""
    if len(row) < 5:
        return row + [""] * len(CLASSIFICATION_COLS)
    key = str(row[3]).strip().lower()
    if key in classification:
        return row + [classification[key][col] for col in CLASSIFICATION_COLS]
    return row + [""] * len(CLASSIFICATION_COLS)


MAX_ROW_LIMIT = 1000


def get_all_sheet_data(spreadsheet_id, sheet_names, credentials):
    service = build("sheets", "v4", credentials=credentials)
    ranges = [f"{name}!A2:O{MAX_ROW_LIMIT}" for name in sheet_names]
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


def is_header_row(row):
    """2번째 컬럼이 '접두'인 헤더성 행인지 확인."""
    return len(row) >= 2 and row[1] == "접두"


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

    classification = load_classification()
    print(f"분류 데이터 {len(classification)}개 로드")

    all_rows = [build_header()]
    total_rows = 0
    header_row_count = 0
    classified_count = 0
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
        if row_count > 1 and row_count + 2 < len(values) - 1:
            values = values[: row_count + 1]  # -1: A2가 시작점이므로
        for row in values:
            if is_header_row(row):
                header_row_count += 1
                continue
            enriched = apply_classification([sheet_name] + row, classification)
            if enriched[-len(CLASSIFICATION_COLS):] != [""] * len(CLASSIFICATION_COLS):
                classified_count += 1
            all_rows.append(enriched)
        total_rows += len(values)
        print(f"  [{sheet_name}] {len(values)}행")

    if header_row_count > 0:
        print(f"헤더성 행 {header_row_count}개 제거")
    print(f"분류 매칭 {classified_count}행 / 총 {total_rows}행 수집 -> {len(all_rows) - 1}행 저장")

    now = datetime.datetime.now()
    new_sheet_name = now.strftime("%Y%m%d_%H%M%S")
    print(f"대상 시트: {DEST_SHEET_ID}")
    print(f"새 시트 이름: {new_sheet_name}")

    create_sheet(DEST_SHEET_ID, new_sheet_name, credentials)
    write_data(DEST_SHEET_ID, new_sheet_name, all_rows, credentials)
