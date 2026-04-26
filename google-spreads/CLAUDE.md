# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 지침

- **모든 답변과 주석은 한글로 작성하세요.**
- 코드 내 주석도 한글로 작성합니다.
- `importlib.util` 동적 임포트는 유지보수를 위해 필요하므로 제거하지 마세요.

## 개요

소스 Google Spreadsheet의 포트폴리오 데이터를 읽어와, 종목을 카테고리(반도체, 빅테크, Fintech, 지역)별로 분류하고, 동적 헤더/수식/서식을 적용하여 대상 스프레드시트에 타임스탬프 시트로 저장하는 Python 스크립트입니다.

## 프로젝트 구조

```
src/
├── lib/                    # 공통 유틸리티
│   ├── auth.py             # Google OAuth2 / Drive API 인증
│   └── sheets.py           # Sheets API v4 헬퍼 + 상수 (스프레드시트 ID, 제외 목록 등)
├── scripts/                # 실행 진입점
│   ├── get-sheet-names.py      # 스프레드시트의 모든 시트 이름 조회
│   ├── get-sheet-details.py    # 모든 시트 데이터 가져와서 출력
│   ├── classification.py       # Google Sheets에서 분류 시트 읽어 자동 분류 후 CSV 저장
│   └── cp_sheet_details.py     # 메인 파이프라인: 소스 시트를 대상으로 복사 + 분류 + 수식 적용
├── data/
│   └── classification.csv      # 자동 생성 종목 분류 룩업 (utf-8-sig 인코딩)
└── docs/
    └── README.md + 스크립트별 설명 문서
```

## 스크립트 실행

모든 스크립트는 `src/` 디렉토리에서 실행해야 합니다:

```bash
cd src

# 서비스 계정 키 설정 (필수)
export GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/google-service-account.json

# 메인 파이프라인 — 소스 시트 읽기, 타임스탬프 대상 시트 생성
python scripts/cp_sheet_details.py

# Google Sheets에서 종목 분류 후 data/classification.csv 저장
python scripts/classification.py

# 소스 스프레드시트의 시트 이름 목록 조회
python scripts/get-sheet-names.py

# 모든 시트 데이터 가져와서 출력
python scripts/get-sheet-details.py
```

## 인증

- Google **서비스 계정** OAuth2를 사용합니다 (사용자 OAuth 아님)
- 기본 키 경로: `investment/google-service-account.json` (`src/lib/`에서 4단계 상위)
- `GOOGLE_SERVICE_ACCOUNT_KEY` 환경변수로 재정의 가능
- 스코프: `drive`, `drive.readonly`

## 주요 상수 (`lib/sheets.py`)

| 상수 | 값 | 용도 |
|---|---|---|
| `SOURCE_SPREADSHEET_ID` | `"1t-4bb...vBGM"` | 포트폴리오 데이터 소스 |
| `DEST_SHEET_ID` | `"1Vqiz...1mg3k"` | 분류 결과가 저장될 대상 |
| `EXCLUDE_SHEETS` | 5개 시트명 | 복사 시 제외 목록 |
| `MAX_ROW_LIMIT` | 1000 | API batchGet 최대 행 제한 |
| `CLASSIFICATION_COLS` | 7개 카테고리 | 반도체, 빅테크, Fintech, 미국, 한국, 중국, World |

## 중요 사항

- **인코딩**: Google Spreadsheet 관련 데이터를 다룰 때 한글이 포함되어 있으므로 항상 `encoding='utf-8-sig'`를 사용하세요. 일반 `utf-8`을 사용하면 BOM 처리 문제로 컬럼명이 깨집니다.
- **`cp_sheet_details.py`**는 `importlib.util`로 `get-sheet-names.py`를 동적 로딩합니다. 하이픈이 포함된 파일명은 표준 `import`로 로드할 수 없습니다.
- **행 수 제한**: `trim_by_row_count()`는 A2 셀의 정수값을 읽어 각 시트의 반환 행 수를 제한하여 불필요한 데이터 전송을 방지합니다.
- **분류 로직**: `cp_sheet_details.py`는 `row[3]`(코드 컬럼, 대소문자 무시)를 `classification.csv`와 매칭합니다. 매칭 성공 시 분류 컬럼에 `=($P{row_num}/$P$1)` 수식을 입력하고, 실패 시 빈 문자열을 넣습니다.
- **헤더 필터링**: `row[1] == "접두"`인 행은 소스 데이터 내의 헤더 행으로 간주하여 건너뜁니다.
- **출력 형식**: 2행 동적 헤더(1행: 오늘 날짜 + SUM 수식, 2행: 컬럼 레이블 + 분류명). Q1:W500은 퍼센트 서식(`0%`), P1은 숫자 서식(`#,##0`).
