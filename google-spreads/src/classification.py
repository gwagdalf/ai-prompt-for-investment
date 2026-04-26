#!/usr/bin/env python3
"""Google Spreadsheet의 classification 시트를 읽고 분류 결과를 CSV로 저장합니다."""

import csv
import os
import sys

from drive_user_info import get_current_user
from googleapiclient.discovery import build

SHEET_ID = "1VqizBSVp7PqmWMFKW9rfzXpg629lenxjWzgwaP1mg3k"
SHEET_NAME = "classification"

OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "classification.csv")

# 분류 키워드 (순서 중요: 먼저 매칭되면 중단)
RULES = {
    "반도체": [
        "반도체", "sk하이닉스", "하이닉스", "삼성전자", "엔비디아", "엔비디아코리아",
        "인텔", "amd", "티에스엠씨", "tsmc", "삼성반도체",
        "tsmc", "필라델피아반도체", "sox", "필라델피아",
    ],
    "빅테크": [
        "빅테크", "애플", "알파벳", "구글", "마이크로소프트", "msft",
        "메타", "아마존", "테슬라", "nvda", "aapl", "googl", "amzn",
        "msft", "meta", "tsla", "naver", "카카오",
        "top7", "top10",
    ],
    "미국": [
        "usa", "us", "미국", "나스닥", "나스닥100", "s&p", "s&p500",
        "nyse", "wall street", "spdr", "qqq", "spy", "ark",
        "미국필라델피아", "미국빅테크", "미국나스닥", "미국s&p",
    ],
    "한국": [
        "krx", "코스피", "코스닥", "korea", "한국", "삼성", "sk", "lg",
        "현대", "기아", "카카오", "naver", "네이버", "메리츠",
        "tiger", "kodex", "ace", "hanaro", "plus", "time", "미래에셋",
        "kgcg", "kscg",
    ],
    "중국": [
        "중국", "china", "상하이", "선전", "항생", "항셍", "h항셍",
        "csi", "csi300", "항셍테크", "항생지수",
        "alibaba", "tencent", "바이두", "xiaomi", "byd", "니오",
    ],
}


def classify_stock(code: str, name: str) -> dict:
    """종목 코드/명으로 분류 플래그를 결정합니다."""
    result = {"반도체": 0, "빅테크": 0, "미국": 0, "한국": 0, "중국": 0, "World": 0}
    search_text = f"{code} {name}".lower()

    for category, keywords in RULES.items():
        for kw in keywords:
            if kw.lower() in search_text:
                result[category] = 1
                break

    # 어느 지역에도 매칭되지 않으면 World
    if result["미국"] == 0 and result["한국"] == 0 and result["중국"] == 0:
        result["World"] = 1

    return result


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    user_info, credentials = get_current_user()
    user = user_info.get("user", {})
    print(f"인증 계정: {user.get('displayName')} ({user.get('emailAddress')})")
    print()

    service = build("sheets", "v4", credentials=credentials)

    # 데이터 읽기
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A:Z",
    ).execute()

    rows = result.get("values", [])
    if not rows:
        print("데이터가 없습니다.")
        return

    header = rows[0]
    print(f"헤더: {header}")
    print(f"총 {len(rows) - 1}행 처리")

    # 컬럼 인덱스 찾기
    code_idx = None
    name_idx = None
    for i, col in enumerate(header):
        if col.strip().lower() in ("코드", "code"):
            if code_idx is None:
                code_idx = i
        if col.strip().lower() in ("종목명", "종목", "name"):
            name_idx = i

    if code_idx is None or name_idx is None:
        print(f"에러: 코드/종목명 컬럼을 찾을 수 없습니다 (code_idx={code_idx}, name_idx={name_idx})")
        return

    print(f"코드 컬럼 인덱스: {code_idx}, 종목명 컬럼 인덱스: {name_idx}")

    # 분류 및 출력 (중복 제거: 코드 기준)
    output_rows = []
    seen_codes = set()
    classified_count = 0

    for row in rows[1:]:
        if not row or all(c.strip() == "" for c in row):
            continue

        code = row[code_idx].strip() if len(row) > code_idx else ""
        name = row[name_idx].strip() if len(row) > name_idx else ""

        if not code and not name:
            continue

        # 코드 중복 제거
        if code.lower() in seen_codes:
            continue
        seen_codes.add(code.lower())

        flags = classify_stock(code, name)
        classified_count += 1

        output_rows.append({
            "코드": code,
            "code": code,
            "종목명": name,
            **flags,
        })

    print(f"분류 완료: {classified_count}개 종목")

    # CSV 저장 (기존 데이터 삭제 후 새로 씀)
    if os.path.exists(OUTPUT_CSV):
        os.remove(OUTPUT_CSV)
        print(f"기존 {OUTPUT_CSV} 데이터 삭제")

    fieldnames = ["코드", "code", "종목명", "반도체", "빅테크", "미국", "한국", "중국", "World"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"새 데이터 저장 완료: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
