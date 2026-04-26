# classification.py

Google Spreadsheet의 classification 시트를 읽고 키워드 기반 종목 분류를 수행하여 `classification.csv`로 저장하는 스크립트입니다.

## 개요

스프레드시트의 `classification` 시트에서 종목 데이터를 읽어, 키워드 매칭을 통해 반도체/빅테크/Fintech/미국/한국/중국/World로 분류합니다. 시트에 기존 분류 값이 있으면 유지하고, 모두 0 또는 공백인 경우에만 자동 분류를 적용합니다.

## 분류 규칙

| 분류 | 키워드 예시 |
|---|---|
| 반도체 | 반도체, SK하이닉스, 삼성전자, 엔비디아, TSMC, 필라델피아반도체, SOX |
| 빅테크 | 애플, 알파벳, 구글, MSFT, 메타, 아마존, 테슬라, NAVER, 카카오, TOP7, TOP10 |
| Fintech | 핀테크, 페이, 토스, 간편결제, 페이팔, PayPal, Block, Square, Stripe |
| 미국 | USA, 미국, 나스닥, S&P500, NYSE, QQQ, SPY, ARK |
| 한국 | KRX, 코스피, 코스닥, 한국, 삼성, SK, TIGER, KODEX, 미래에셋 |
| 중국 | 중국, China, 상하이, 선전, 항셍, CSI300, 알리바바, 텐센트 |
| World | 위 분류에 매칭되지 않는 종목 |

## 주요 함수

### `classify_stock(code, name)`

종목 코드/명으로 분류 플래그를 결정합니다.

- **파라미터**:
  - `code`: 종목 코드
  - `name`: 종목명
- **반환값**: `dict` — 각 분류 컬럼별 0/1 플래그

### `main()`

스프레드시트에서 데이터 읽기 → 중복 제거 → 기존 분류 유지 또는 자동 분류 → CSV 저장까지의 전체 파이프라인을 실행합니다.

## 출력 파일

- `classification.csv` — BOM 포함 UTF-8 (`utf-8-sig`)로 저장

## 중복 처리

`코드` 기준 중복을 제거합니다 (대소문자 무시, 처음 등장하는 종목만 유지).

## 의존성

- `drive_user_info.get_current_user`
- `googleapiclient.discovery`
