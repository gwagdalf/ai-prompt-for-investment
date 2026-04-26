# Google Drive & Sheets API 키 생성 및 권한 설정 가이드

## 개요

이 가이드는 **Google Drive API**와 **Google Sheets API**를 사용하여 스프레드시트 데이터를 읽고 쓰는 애플리케이션을 개발하기 위한 인증/권한 설정 절차를 설명합니다.

> **중요**: Google Sheets 데이터를 **수정(쓰기)** 하려면 API Key만으로는 부족하며, **OAuth 2.0** 또는 **Service Account**가 필요합니다.

---

## 1단계: Google Cloud 프로젝트 생성

### 1.1 Google Cloud Console 접속

1. 브라우저에서 [https://console.cloud.google.com](https://console.cloud.google.com) 접속
2. Google 계정으로 로그인 (개인 Gmail 또는 Workspace 계정)
3. 첫 방문 시 이용약관에 동의

### 1.2 새 프로젝트 생성

1. 상단 프로젝트 선택기 클릭 (현재 프로젝트 이름 표시됨)
2. **"새 프로젝트"** 버튼 클릭
3. 프로젝트 이름 입력 (예: `investment-sheet-app`)
4. 조직은 `(없음)` 으로 선택 (개인 프로젝트인 경우)
5. **"만들기"** 클릭 → 프로젝트 생성 완료 (몇 초 소요)
6. 생성된 프로젝트가 자동으로 선택됨 (선택 안 되었으면 수동 선택)

---

## 2단계: API 활성화

### 2.1 Google Drive API 활성화

1. 좌측 메뉴 → **"API 및 서비스"** → **"라이브러리"** 클릭
   - 또는 직접 접속: `https://console.cloud.google.com/apis/library`
2. 검색창에 `Google Drive API` 입력
3. **"Google Drive API"** 결과 클릭
4. **"사용 설정"** 버튼 클릭

### 2.2 Google Sheets API 활성화

1. 동일하게 **"라이브러리"**에서 `Google Sheets API` 검색
2. **"Google Sheets API"** 결과 클릭
3. **"사용 설정"** 버튼 클릭

> 두 API 모두 "사용 설정됨" 상태여야 합니다.

---

## 3단계: 인증 방식 선택

애플리케이션의 사용 목적에 따라 **세 가지 인증 방식** 중 선택합니다.

| 방식 | 읽기 전용 | 쓰기 가능 | 설명 |
|------|:---------:|:---------:|------|
| **API Key** | ✅ | ❌ | 공개 데이터 읽기 전용 |
| **OAuth 2.0** | ✅ | ✅ | 내 Google 계정 권한으로 내 시트 접근 |
| **Service Account** | ✅ | ✅ | 서버 간 자동화, 별도 계정 생성 |

### 선택 가이드

- **나만의 시트를 내가 직접 읽고 쓰기**: → **OAuth 2.0** (권장)
- **서버/봇이 자동으로 시트 읽고 쓰기**: → **Service Account**
- **공개 시트 읽기 전용**: → **API Key**

> **Spreadsheet 데이터 수정이 목적이므로 OAuth 2.0 또는 Service Account가 필요합니다.**

---

## 4단계 (A): OAuth 2.0 설정 — 내 계정 권한으로 시트 접근

개인 애플리케이션에서 **내 자신의 Google Sheet**에 접근하는 경우 이 방식을 사용합니다.

### 4A.1 OAuth 동의 화면 설정

1. 좌측 메뉴 → **"API 및 서비스"** → **"OAuth 동의 화면"**
   - 또는: `https://console.cloud.google.com/apis/credentials/consent`
2. **사용자 유형 선택**:
   - **외부**: 일반 Gmail 계정 사용 (권장 — 누구나 테스트 가능)
   - **내부**: Google Workspace 조직 내 사용자만
3. **"만들기"** 클릭

### 4A.2 앱 정보 입력

| 필드 | 입력값 |
|------|--------|
| 앱 이름 | `Investment Sheet App` (원하는 이름) |
| 사용자 지원 이메일 | 내 Gmail 주소 선택 |
| 개발자 연락처 정보 | 내 Gmail 주소 |

4. **"저속하고 계속"** 클릭

### 4A.3 범위(Scopes) 추가

1. **"범위 추가 또는 삭제"** 클릭
2. 다음 범위 검색 후 추가:

   | 범위 | 권한 |
   |------|------|
   | `.../auth/drive.readonly` | Drive 파일 읽기 |
   | `.../auth/drive` | Drive 전체 접근 |
   | `.../auth/spreadsheets` | Sheets 읽기/쓰기 |
   | `.../auth/spreadsheets.readonly` | Sheets 읽기 전용 |

   > **권장**: `https://www.googleapis.com/auth/spreadsheets` (Sheets 읽기+쓰기)
   >
   > Drive 파일 목록까지 접근하려면 `https://www.googleapis.com/auth/drive` 추가

3. **"업데이트"** → **"저속하고 계속"**

### 4A.4 테스트 사용자 추가 (외부 모드인 경우)

1. **"테스트 사용자"** 섹션에서 **"사용자 추가"** 클릭
2. 내 Gmail 주소 입력 (앱을 사용할 계정들 추가)
3. **"저속하고 계속"** → 요약 확인 → **"뒤로 대시보드"**

### 4A.5 OAuth 2.0 클라이언트 ID 생성

1. 좌측 메뉴 → **"API 및 서비스"** → **"사용자 인증 정보"**
   - 또는: `https://console.cloud.google.com/apis/credentials`
2. **"+ 사용자 인증 정보 만들기"** → **"OAuth 클라이언트 ID"** 클릭
3. **애플리케이션 종류** 선택:

   | 종류 | 용도 |
   |------|------|
   | **데스크탑 앱** | Python/Node.js 로컬 스크립트 (권장) |
   | **웹 애플리케이션** | 웹 서버, 백엔드 API |

4. 이름 입력 (예: `Investment Desktop Client`)
5. **"만들기"** 클릭

### 4A.6 인증 정보 다운로드

1. 생성 완료 후 팝업에서 **"JSON 다운로드"** 클릭
2. 파일명 예: `credentials.json`
3. 이 파일을 프로젝트 루트에 저장

```
your-project/
├── credentials.json     ← 다운로드한 OAuth 인증 파일
├── token.json           ← 첫 로그인 후 자동 생성 (재사용)
└── main.py
```

> **주의**: `credentials.json`은 민감 정보이므로 `.gitignore`에 추가하세요.

### 4A.7 첫 실행 및 토큰 발급

1. 애플리케이션 최초 실행 시 브라우저가 열리며 Google 로그인 요청
2. 로그인 후 **"권한 허용"** 클릭
3. 승인 코드 자동 수신 → `token.json` 파일로 저장
4. **이후 실행부터는 `token.json`으로 자동 인증** (재로그인 불필요)

---

## 4단계 (B): Service Account 설정 — 서버 간 자동화

서버/백그라운드에서 자동으로 Sheets에 접근하는 경우 사용합니다.

### 4B.1 서비스 계정 생성

1. 좌측 메뉴 → **"API 및 서비스"** → **"사용자 인증 정보"**
2. **"+ 사용자 인증 정보 만들기"** → **"서비스 계정"** 클릭
3. 서비스 계정 이름 입력 (예: `investment-sheet-bot`)
4. **"만들기 및 계속"**
5. 역할 선택: **없음** (Drive/Sheets 권한은 시트 공유로 부여)
6. **"완료"**

### 4B.2 키(JSON) 생성

1. 생성된 서비스 계정 클릭
2. **"키"** 탭 → **"키 추가"** → **"새 키 만들기"**
3. **JSON** 선택 → **"만들기"**
4. JSON 파일 자동 다운로드 (예: `investment-sheet-bot-xxxxx.json`)
5. 프로젝트에 저장

### 4B.3 Google Sheet 공유 (매우 중요!)

> **서비스 계정은 시트에 대한 권한이 없습니다. 시트 소유자가 명시적으로 공유해야 합니다.**

1. Google Sheets에서 대상 스프레드시트 열기
2. 오른쪽 상단 **"공유"** 버튼 클릭
3. 서비스 계정 이메일 주소 입력
   - JSON 파일의 `client_email` 값 (예: `investment-sheet-bot@xxx.iam.gserviceaccount.com`)
4. 권한: **"편집자"** (쓰기 필요 시) 또는 **"조회자"** (읽기 전용)
5. **"공유"** 클릭

### 4B.4 서비스 계정 파일 구조

```
your-project/
├── service-account.json    ← 다운로드한 서비스 계정 키
└── main.py
```

> **주의**: 서비스 계정 키 파일은 절대 공개 저장소에 커밋하지 마세요. `.gitignore`에 추가하세요.

---

## 5단계: Python 라이브러리 설치

### OAuth 2.0 방식

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Service Account 방식

```bash
pip install --upgrade google-api-python-client google-auth
```

### 공통: gspread 라이브러리 (추천 — Sheets 전용 간편 라이브러리)

```bash
pip install --upgrade gspread google-auth
```

---

## 6단계: 코드 예제

### 6.1 OAuth 2.0 — Sheets 읽기/쓰기

```python
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 필요한 범위
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
]

SPREADSHEET_ID = '시트ID를_입력하세요'  # URL에서 /d/다음 부분

def get_credentials():
    creds = None
    # token.json: 이전 실행에서 저장된 토큰
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 유효하지 않으면 재인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # 새 토큰 저장
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def main():
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # 읽기
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Sheet1!A1:D10'
    ).execute()
    values = result.get('values', [])
    print("읽은 데이터:", values)

    # 쓰기
    body = {'values': [['2026-04-26', '삼성전자', '60000', '매수']]}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='Sheet1!A1',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    print("데이터 쓰기 완료")

    # 업데이트 (특정 셀)
    body = {'values': [['61000']]}
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Sheet1!C2',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    print("데이터 업데이트 완료")

if __name__ == '__main__':
    main()
```

### 6.2 Service Account — Sheets 읽기/쓰기 (gspread 사용)

```python
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = '시트ID를_입력하세요'

def main():
    # 서비스 계정 인증
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]
    creds = Credentials.from_service_account_file(
        'service-account.json', scopes=scopes)

    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.worksheet('Sheet1')

    # 읽기
    all_values = worksheet.get_all_values()
    print("모든 데이터:", all_values)

    # 특정 셀 읽기
    cell_value = worksheet.acell('A1').value
    print("A1 값:", cell_value)

    # 쓰기 (단일 셀)
    worksheet.update('A1', '2026-04-26')

    # 쓰기 (범위)
    worksheet.update('A2:D2', [['삼성전자', '60000', '매수', '100']])

    # 행 추가
    worksheet.append_row(['2026-04-27', 'SK하이닉스', '180000', '매도', '50'])

    print("완료!")

if __name__ == '__main__':
    main()
```

### 6.3 gspread + OAuth 2.0 (간편 방식)

```python
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

def get_gspread_client():
    creds = None
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as f:
            f.write(creds.to_json())

    return gspread.authorize(creds)

def main():
    gc = get_gspread_client()
    sh = gc.open_by_key('시트ID를_입력하세요')
    ws = sh.worksheet('Sheet1')

    # 데이터 읽기
    print(ws.get_all_records())

    # 데이터 쓰기
    ws.append_row(['새로운', '데이터', '행'])

    print("완료!")

if __name__ == '__main__':
    main()
```

---

## 7단계: 스프레드시트 ID 확인 방법

1. Google Sheets에서 대상 시트 열기
2. URL에서 `/d/` 와 `/edit` 사이 부분이 **스프레드시트 ID**

```
https://docs.google.com/spreadsheets/d/1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1u/edit#gid=0
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                           이 부분이 ID
```

---

## 8단계: 보안 가이드라인

### `.gitignore`에 추가

```gitignore
# Google 인증 파일
credentials.json
token.json
service-account.json
*.json
```

### 환경 변수 활용 (프로덕션)

```bash
# .env 파일
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export SPREADSHEET_ID="your-spreadsheet-id"
```

```python
import os

# Service Account: 환경 변수에서 자동 감지
creds = Credentials.from_service_account_info(
    json.loads(os.environ['GOOGLE_CREDENTIALS_JSON'])
)
```

---

## 9단계: 문제 해결

| 문제 | 해결 방법 |
|------|-----------|
| `unauthorized_client` | OAuth 동의 화면에서 범위 추가 확인 |
| `access_denied` | OAuth 테스트 사용자 추가 확인 또는 앱 게시 |
| `PERMISSION_DENIED` (Service Account) | 시트에 서비스 계정 이메일 공유 |
| `invalid_grant` | `token.json` 삭제 후 재인증 |
| `The caller does not have permission` | API 콘솔에서 Sheets API 활성화 확인 |
| `quota exceeded` | API 할당량 확인 (Console → API 및 서비스 → 할당량) |

---

## 요약: 추천 구성

| 시나리오 | 인증 방식 |
|----------|-----------|
| **내 시트에 내 계정 권한으로 접근** | OAuth 2.0 + `credentials.json` |
| **서버 자동화 / 백그라운드 작업** | Service Account + JSON 키 + 시트 공유 |
| **공개 데이터 읽기 전용** | API Key |

> **Spreadsheet 데이터 수정이 목표이므로, 개인용이면 OAuth 2.0, 서버용이면 Service Account를 사용하세요.**
