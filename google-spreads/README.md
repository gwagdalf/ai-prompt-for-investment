# Google Spreadsheets Tools

Google Spreadsheet API를 사용하여 스프레드시트 데이터를 조회, 분류, 복사하는 도구 모음입니다.

## 파일 목록

| 파일 | 설명 |
|---|---|
| [drive_user_info.py](src/docs/drive_user_info.py.md) | Google Drive API 인증 및 현재 사용자 정보 조회 모듈 |
| [get-sheet-names.py](src/docs/get-sheet-names.py.md) | 스프레드시트의 시트 이름 목록 조회 |
| [get-sheet-details.py](src/docs/get-sheet-details.py.md) | 모든 시트의 상세 데이터 조회 및 콘솔 출력 |
| [classification.py](src/docs/classification.py.md) | 키워드 기반 종목 분류 → `classification.csv` 생성 |
| [cp_sheet_details.py](src/docs/cp_sheet_details.py.md) | 소스 시트 데이터를 대상 스프레드시트로 복사 + 분류 + 서식 적용 |

## 사용 흐름

```
1. drive_user_info.py     → 인증 (공통 모듈)
2. get-sheet-names.py     → 시트 목록 확인
3. get-sheet-details.py   → 데이터 확인
4. classification.py      → 분류 데이터 생성 (classification.csv)
5. cp_sheet_details.py    → 대상 스프레드시트로 복사 + 분류 + 서식 적용
```

## 환경 설정

- 서비스 계정 키 파일: `google-service-account.json` (프로젝트 루트 기준 상위 경로)
- 또는 `GOOGLE_SERVICE_ACCOUNT_KEY` 환경변수로 경로 지정
