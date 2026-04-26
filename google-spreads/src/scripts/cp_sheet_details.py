#!/usr/bin/env python3
"""get-sheet-details.py 데이터를 읽어 대상 스프레드시트에 복사합니다."""

import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.auth import get_current_user, print_auth_info
from lib.sheets import (
    SOURCE_SPREADSHEET_ID,
    DEST_SHEET_ID,
    EXCLUDE_SHEETS,
    CLASSIFICATION_COLS,
    get_all_sheet_data,
    trim_by_row_count,
    create_sheet,
    write_data,
    format_percentage_range,
)

# get-sheet-names.py에서 get_sheet_names 함수 임포트
_script_dir = os.path.dirname(os.path.abspath(__file__))
_gsn_path = os.path.join(_script_dir, "get-sheet-names.py")
import importlib.util
_gsn_spec = importlib.util.spec_from_file_location("get_sheet_names", _gsn_path)
_gsn_mod = importlib.util.module_from_spec(_gsn_spec)
_gsn_spec.loader.exec_module(_gsn_mod)
get_sheet_names = _gsn_mod.get_sheet_names

CLASSIFICATION_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "classification.csv")


def build_header():
    """두 줄의 동적 헤더를 생성합니다."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    return [
        ["계좌", "#", "접두", "코드", "code", today, "수량", "평균단가", "현재가", "수익률", "매입금액", "평가금액", "평가손익", "통화", "환율", "=SUM(P2:P500)", "=SUM(Q2:Q500)", "=SUM(R2:R500)", "=SUM(S2:S500)", "=SUM(T2:T500)", "=SUM(U2:U500)", "=SUM(V2:V500)", "=SUM(W2:W500)"],
        ["계좌", "#", "접두", "코드", "code", "종목명", "수량", "평균단가", "현재가", "수익률", "매입금액", "평가금액", "평가손익", "통화", "환율", "원평가", "반도체", "빅테크", "Fintech", "미국", "한국", "중국", "World"],
    ]


def load_classification():
    """classification.csv를 읽어 코드 → 분류값 매핑을 반환합니다."""
    lookup = {}
    try:
        with open(CLASSIFICATION_CSV, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row.get("코드", "").strip().lower()
                lookup[key] = {col: row.get(col, "0") for col in CLASSIFICATION_COLS}
    except FileNotFoundError:
        print(f"경고: {CLASSIFICATION_CSV} 파일을 찾을 수 없습니다.")
    return lookup


def is_header_row(row):
    """2번째 컬럼이 '접두'인 헤더성 행인지 확인."""
    return len(row) >= 2 and row[1] == "접두"


def apply_classification(row, classification, row_num):
    """row[3](코드)로 분류 데이터를 매핑하여 컬럼을 추가합니다.
    매칭 시 =($P{row_num}/$P$1) 수식을 입력합니다.
    """
    padded = list(row)
    key = str(row[3]).strip().lower()
    if key in classification:
        padded += [
            f"=($P{row_num}/$P$1)" if classification[key][col] == "1" else ""
            for col in CLASSIFICATION_COLS
        ]
    else:
        padded += [""] * len(CLASSIFICATION_COLS)
    return padded


if __name__ == "__main__":
    user_info, credentials = get_current_user()
    print_auth_info(user_info)

    all_sheet_names = get_sheet_names(SOURCE_SPREADSHEET_ID, credentials)
    target_sheets = [name for name in all_sheet_names if name not in EXCLUDE_SHEETS]
    print(f"전체 시트: {len(all_sheet_names)}개 / 처리 대상: {len(target_sheets)}개 (제외: {len(EXCLUDE_SHEETS)}개)")

    print("소스 시트 데이터 가져오는 중...")
    batch_results = get_all_sheet_data(SOURCE_SPREADSHEET_ID, target_sheets, credentials)

    classification = load_classification()
    print(f"분류 데이터 {len(classification)}개 로드")

    all_rows = build_header()
    total_rows = 0
    header_row_count = 0
    classified_count = 0
    output_row = 2
    for sheet_name, sheet_data in zip(target_sheets, batch_results):
        values = sheet_data.get("values", [])
        if not values:
            continue
        values = trim_by_row_count(values)
        for row in values:
            if is_header_row(row):
                header_row_count += 1
                continue
            output_row += 1
            enriched = apply_classification([sheet_name] + row, classification, output_row)
            if any(enriched[-len(CLASSIFICATION_COLS):]):
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
    format_percentage_range(DEST_SHEET_ID, new_sheet_name, credentials)
