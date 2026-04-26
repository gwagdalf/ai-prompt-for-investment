# Google Spreadsheets Tools

Google Sheets API를 사용하여 포트폴리오 데이터를 조회, 종목 분류, 대상 스프레드시트로 복사하는 도구 모음입니다.

## 프로젝트 구조

```
google-spreads/
├── CLAUDE.md                          # AI 개발 가이드
├── README.md                          # 프로젝트 소개
├── google-drive-*.md                  # API 키 설정 가이드
└── src/
    ├── lib/                           # 공통 유틸리티
    │   ├── auth.py                    # Google OAuth2 / Drive API 인증
    │   └── sheets.py                  # Sheets API 헬퍼 + 상수 정의
    ├── scripts/                       # 실행 스크립트
    │   ├── get-sheet-names.py         # 시트 목록 조회
    │   ├── get-sheet-details.py       # 시트 데이터 조회
    │   ├── classification.py          # 종목 분류 → CSV 저장
    │   └── cp_sheet_details.py        # 메인 파이프라인 (복사 + 분류 + 서식)
    ├── data/
    │   └── classification.csv         # 종목 분류 데이터 (자동 생성)
    └── docs/
        └── *.md                       # 스크립트별 상세 문서
```

## 사용 흐름

```
1. lib/auth.py          → 인증 설정 (공통 모듈)
2. get-sheet-names.py   → 시트 목록 확인
3. get-sheet-details.py → 데이터 미리보기
4. classification.py    → 분류 데이터 생성 (classification.csv)
5. cp_sheet_details.py  → 대상 스프레드시트로 복사 + 분류 + 서식 적용
```

## 환경 설정

1. Google 서비스 계정 JSON 키를 준비합니다.
2. `GOOGLE_SERVICE_ACCOUNT_KEY` 환경변수에 파일 경로를 설정합니다:

   ```bash
   export GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/google-service-account.json
   ```

   설정하지 않으면 `investment/google-service-account.json` (프로젝트 루트 기준 상위)에서 찾습니다.

## 스크립트 실행

모든 스크립트는 `src/` 디렉토리에서 실행합니다:

```bash
cd src

# 시트 목록 조회
python scripts/get-sheet-names.py

# 시트 데이터 조회
python scripts/get-sheet-details.py

# 종목 분류 CSV 생성
python scripts/classification.py

# 메인 파이프라인: 소스 → 대상 복사 + 분류 + 서식
python scripts/cp_sheet_details.py
```

## 분류 카테고리

7개 카테고리에서 키워드 매칭으로 종목을 분류합니다:

| 카테고리 | 예시 키워드 |
|---|---|
| 반도체 | 반도체, SK하이닉스, 삼성전자, 엔비디아, TS MC |
| 빅테크 | 애플, 알파벳, 마이크로소프트, 메타, 아마존, 네이버, 카카오 |
| Fintech | 핀테크, 페이, 토스, PayPal, Block, Stripe |
| 미국 | USA, 나스닥, S&P500, QQQ |
| 한국 | 한국, 삼성, SK, LG, 현대 |
| 중국 | 중국, 알리바바, 텐센트, BYD |
| World | 미국/한국/중국 외 지역 |

## 중요 사항

- **인코딩**: 한글 포함 파일은 반드시 `encoding='utf-8-sig'`를 사용하세요.
- **종류된 스크립트**: 하이픈이 포함된 파일명(`get-sheet-names.py` 등)은 `importlib.util`로 동적 로딩합니다.
- **자동 분류**: `cp_sheet_details.py`는 `classification.csv`의 "코드" 컬럼을 매칭하여 분류 수식을 적용합니다.
