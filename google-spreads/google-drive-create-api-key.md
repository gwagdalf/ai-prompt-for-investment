# Google Drive & Sheets API ACCESS_TOKEN 발급 가이드 (초보자용)

## 목표

아래 curl 명령어에서 `[ACCESS_TOKEN_값_여기에_입력]` 부분에 들어갈 토큰을 직접 만들어 봅니다.

```bash
curl -X GET \
  "https://www.googleapis.com/drive/v3/about?fields=user" \
  -H "Authorization: Bearer [ACCESS_TOKEN_값_여기에_입력]"
```

> **핵심**: ACCESS_TOKEN은 "내 Google 계정으로 이 작업을 해도 된다"는 **디지털 신분증**입니다.
> 만료 기간이 있어서 보통 1시간마다 새 토큰을 받아야 합니다.

---

## 사전 준비: Google Cloud 프로젝트 만들기 (10분)

### 1단계: Google Cloud Console 접속

1. 브라우저에서 다음 주소로 이동합니다:
   ```
   https://console.cloud.google.com
   ```
2. Google 계정으로 로그인합니다 (평소 쓰는 Gmail 계정)

### 2단계: 새 프로젝트 생성

1. 페이지 **맨 위**에 파란색 바가 있습니다. 프로젝트 이름이 표시된 곳을 클릭합니다.

   ```
   ┌──────────────────────────────────────────────────┐
   │  ≡  Google Cloud  [🔽 내 프로젝트]  [검색...]  │
   └──────────────────────────────────────────────────┘
                          ↑ 여기를 클릭
   ```

2. 팝업 창 오른쪽 위에서 **"새 프로젝트"** 버튼을 클릭합니다.
3. 프로젝트 이름을 입력합니다 (예: `my-drive-app`)
4. **"만들기"** 버튼을 클릭합니다.
5. 5~10초 기다린 뒤, 종 모양 아이콘(알림)을 클릭하여 **"작성 완료"**를 확인합니다.
6. 프로젝트 선택기에서 방금 만든 프로젝트를 클릭하여 선택합니다.

### 3단계: Drive API와 Sheets API 사용 설정

1. 상단 검색창에 `Google Drive API`를 입력하고 엔터를 누릅니다.
2. 검색 결과에서 **"Google Drive API"**를 클릭합니다.
3. 파란색 **"사용 설정"** 버튼을 클릭합니다.
4. 같은 방법으로 `Google Sheets API`도 검색해서 **"사용 설정"**을 클릭합니다.

   ```
   ✅ Google Drive API → "사용 설정됨" 표시 확인
   ✅ Google Sheets API → "사용 설정됨" 표시 확인
   ```

### 4단계: OAuth 동의 화면 설정

1. 좌측 메뉴에서 **"API 및 서비스"**를 클릭합니다. 마우스를 올리면 하위 메뉴가 나옵니다.
2. **"OAuth 동의 화면"**을 클릭합니다.
   - 바로 가기: `https://console.cloud.google.com/apis/credentials/consent`
3. **"외부"**를 선택하고 **"만들기"**를 클릭합니다.
   > "외부"란: 내 개인 Gmail 계정을 사용한다는 의미입니다.
4. 다음 정보를 입력합니다:

   | 항목 | 입력값 |
   |------|--------|
   | 앱 이름 | `My Drive App` (아무거나) |
   | 사용자 지원 이메일 | 드롭다운에서 내 Gmail 선택 |
   | 개발자 연락처 정보 | 내 Gmail 주소 입력 |

5. **"저장하고 계속"**을 세 번 클릭하여 나머지 단계를 건너뜁니다.
6. **"대시보드"**로 돌아옵니다.

### 5단계: 테스트 사용자 추가

1. 방금 설정한 페이지 아래로 스크롤하여 **"테스트 사용자"** 섹션을 찾습니다.
2. **"사용자 추가"** 버튼을 클릭합니다.
3. 내 Gmail 주소를 입력합니다 (예: `myname@gmail.com`)
4. Enter를 누르고 **"저장하고 계속"** → **"대시보드"**

---

## 방법 1: OAuth 2.0 Playground로 빠르게 토큰 받기 (5분, 테스트용)

> 가장 쉬운 방법입니다. 브라우저에서 클릭 몇 번으로 토큰을 받을 수 있습니다.
> 단, 토큰이 **1시간** 후에 만료되므로 매번 새로 받아야 합니다.

### 1.1 OAuth 2.0 Playground 열기

브라우저에서 다음 주소로 이동합니다:

```
https://developers.google.com/oauthplayground/
```

### 1.2 범위(Scope) 추가

1. 페이지 왼쪽에 **"Step 1: Select & authorize APIs"** 섹션이 있습니다.
2. 검색창에 `Google Drive API v3`를 입력합니다.
3. 나타나는 목록에서 다음을 체크합니다:
   - `https://www.googleapis.com/auth/drive` (Drive 전체 접근)
4. 검색창에 `Google Sheets API v4`를 입력합니다.
5. 나타나는 목록에서 다음을 체크합니다:
   - `https://www.googleapis.com/auth/spreadsheets` (Sheets 읽기/쓰기)
6. **"+ Authorize APIs"** 버튼을 클릭합니다.

   ```
   화면 예시:
   ┌─────────────────────────────────────────────────┐
   │ Step 1: Select & authorize APIs                 │
   │                                                 │
   │ [Google Drive API v3 ▼]                         │
   │   ☑ https://www.googleapis.com/auth/drive       │
   │                                                 │
   │ [Google Sheets API v4 ▼]                        │
   │   ☑ https://www.googleapis.com/auth/spreadsheets│
   │                                                 │
   │            [+ Authorize APIs]  ← 클릭!          │
   └─────────────────────────────────────────────────┘
   ```

### 1.3 Google 계정 로그인 및 권한 허용

1. 새 창이 열리며 **"계정을 선택하세요"**가 나옵니다.
2. 내 Google 계정을 클릭합니다.
3. **"확인"** 또는 **"허용"** 버튼을 클릭합니다.
   > "이 앱이 다음 권한을 요청합니다: 내 Google Drive 파일 보기 및 관리, 내 스프레드시트 보기 및 관리"
4. 다시 OAuth Playground 페이지로 돌아옵니다.

### 1.4 ACCESS_TOKEN 받기

1. 페이지 왼쪽 **"Step 2: Configure request to API"** 섹션을 확인합니다.
2. **"Exchange authorization code for tokens"** 버튼을 클릭합니다.
3. **"Step 2"** 박스가 열리면서 여러 정보가 표시됩니다:

   ```
   ┌─────────────────────────────────────────────────┐
   │ Step 2: Configure request to API               │
   │                                                 │
   │ access_token:                                   │
   │ ya29.a0Ae... (이것이 ACCESS_TOKEN!)             │
   │                                                 │
   │ refresh_token: 1//0gX... (재발급용)             │
   │ expires_in: 3599 (3600초 = 1시간)               │
   │                                                 │
   │ [Refresh token]  ← 1시간 후 이걸로 새로 받기    │
   └─────────────────────────────────────────────────┘
   ```

4. **`access_token`** 값을 복사합니다. `ya29.a0Ae...` 로 시작하는 긴 문자열입니다.

### 1.5 curl 명령어에 넣기

복사한 토큰을 아래 명령어에 붙여넣습니다:

```bash
curl -X GET \
  "https://www.googleapis.com/drive/v3/about?fields=user" \
  -H "Authorization: Bearer ya29.a0Ae...방금_복사한_토큰..."
```

### 1.6 성공 결과 확인

성공하면 이런 결과가 나옵니다:

```json
{
  "kind": "drive#about",
  "user": {
    "kind": "drive#user",
    "displayName": "홍길동",
    "photoLink": "https://lh3.googleusercontent.com/...",
    "me": true,
    "permissionId": "12345678901234567890",
    "emailAddress": "myname@gmail.com"
  }
}
```

### ⚠️ 주의사항

- **1시간 후 토큰이 만료**됩니다. 만료되면 다시 1.4로 돌아가서 **"Exchange authorization code for tokens"**를 누르면 새 토큰을 받을 수 있습니다.
- 이 방법은 **테스트/확인용**입니다. 자동화에는 적합하지 않습니다.

---

## 방법 2: Service Account로 토큰 발급 (자동화용, 권장)

> 프로그램에서 자동으로 토큰을 발급받아 사용합니다.
> 한번 설정하면 **token.json, refresh_token 관리가 불필요**합니다.

### 2.1 서비스 계정 만들기

1. Google Cloud Console에서 **"API 및 서비스"** → **"사용자 인증 정보"**로 이동합니다.
   - 바로 가기: `https://console.cloud.google.com/apis/credentials`
2. **"+ 사용자 인증 정보 만들기"** 버튼을 클릭합니다.
3. **"서비스 계정"**을 선택합니다.
4. 다음 정보를 입력합니다:

   | 항목 | 입력값 |
   |------|--------|
   | 서비스 계정 이름 | `drive-sheets-bot` |
   | 서비스 계정 ID | 자동 입력됨 (수정 불필요) |
   | 설명 | `Drive & Sheets API 접근용` |

5. **"만들고 계속"**을 클릭합니다.
6. **역할 선택 화면**: 아무것도 선택하지 않고 **"계속"** → **"완료"**를 클릭합니다.
   > Drive/Sheets 권한은 시트 공유로 따로 부여합니다.

### 2.2 JSON 키 파일 다운로드

1. 방금 만든 서비스 계정(`drive-sheets-bot`)을 클릭합니다.
2. **"키"** 탭을 클릭합니다.
3. **"키 추가"** → **"새 키 만들기"**를 클릭합니다.
4. **`JSON`**을 선택하고 **"만들기"**를 클릭합니다.
5. JSON 파일이 다운로드됩니다 (예: `my-drive-app-12345-abc.json`)
6. 이 파일을 작업 폴더에 복사합니다.

   ```bash
   # 예시: 다운로드 폴더에서 작업 폴더로 복사
   cp ~/Downloads/my-drive-app-12345-abc.json ./service-account.json
   ```

### 2.3 JSON 파일 내용 확인

다운로드한 JSON 파일을 열어보면 이런 내용이 있습니다:

```json
{
  "type": "service_account",
  "project_id": "my-drive-app-12345",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n",
  "client_email": "drive-sheets-bot@my-drive-app-12345.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

> **중요**: `client_email` 값을 메모해 둡니다. 시트 공유에 필요합니다.

### 2.4 Google Sheet에 서비스 계정 공유 (매우 중요!)

> 서비스 계정은 가상의 계정입니다. 내 시트에 대한 권한이 **전혀 없습니다**.
> 시트 소유자가 직접 공유해 줘야 합니다.

1. Google Sheets에서 대상 스프레드시트를 엽니다.
2. 오른쪽 위 **"공유"** 버튼을 클릭합니다.
3. JSON 파일의 `"client_email"` 값을 붙여넣습니다.
   ```
   예: drive-sheets-bot@my-drive-app-12345.iam.gserviceaccount.com
   ```
4. 권한을 **"편집자"**로 선택합니다 (쓰기 필요 시).
5. **"공유"** 버튼을 클릭합니다.

### 2.5 토큰 발급 (CLI 방식)

가장 쉬운 방법은 `gcloud` CLI를 사용하는 것입니다:

```bash
# gcloud로 토큰 발급
gcloud auth activate-service-account --key-file=./service-account.json

# ACCESS_TOKEN 받기
gcloud auth print-access-token
```

출력 예시:
```
ya29.c... (긴 문자열)
```

이제 curl에 사용합니다:

```bash
ACCESS_TOKEN=$(gcloud auth print-access-token)

curl -X GET \
  "https://www.googleapis.com/drive/v3/about?fields=user" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 2.6 토큰 발급 (Python 방식 — gcloud 미설치 시)

gcloud가 설치되어 있지 않다면 Python으로 토큰을 발급받습니다:

```bash
# 필요한 라이브러리 설치
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

```python
#!/usr/bin/env python3
"""service_account 토큰 발급 스크립트"""

from google.oauth2.service_account import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]

# 토큰 발급
creds = Credentials.from_service_account_file(
    './service-account.json',
    scopes=SCOPES
)

# 만료되었으면 자동 갱신
if not creds.valid:
    import google.auth.transport.requests
    request = google.auth.transport.requests.Request()
    creds.refresh(request)

print("ACCESS_TOKEN:")
print(creds.token)
```

실행:
```bash
python get_token.py
```

출력된 토큰을 curl에 사용합니다:
```bash
curl -X GET \
  "https://www.googleapis.com/drive/v3/about?fields=user" \
  -H "Authorization: Bearer ya29.c...출력된_토큰..."
```

### 2.7 토큰 발급 (pure curl + jq 방식)

JSON 파일에서 직접 토큰을 발급받는 curl 명령어도 가능합니다 (고급):

```bash
# service-account.json 에서 필요한 값 추출
CLIENT_EMAIL=$(python3 -c "import json; print(json.load(open('service-account.json'))['client_email'])")
PRIVATE_KEY=$(python3 -c "import json; print(json.load(open('service-account.json'))['private_key'])")

# Python 한 줄로 JWT 서명 및 토큰 발급
python3 -c "
from google.oauth2.service_account import Credentials
creds = Credentials.from_service_account_file('./service-account.json',
    scopes=['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets'])
import google.auth.transport.requests
creds.refresh(google.auth.transport.requests.Request())
print(creds.token)
"
```

---

## 방법 3: OAuth 2.0 Client ID로 토큰 발급 (내 개인 계정용)

> 서비스 계정 대신 **내 개인 Gmail 계정** 권한으로 토큰을 발급받습니다.
> 브라우저 로그인 → 토큰 수신 → curl 사용 흐름입니다.

### 3.1 OAuth 클라이언트 ID 만들기

1. Google Cloud Console → **"API 및 서비스"** → **"사용자 인증 정보"**
   - `https://console.cloud.google.com/apis/credentials`
2. **"+ 사용자 인증 정보 만들기"** → **"OAuth 클라이언트 ID"**
3. 애플리케이션 종류에서 **"데스크톱 앱"** 선택
4. 이름 입력: `My Drive CLI`
5. **"만들기"** 클릭

### 3.2 인증 정보 다운로드

1. 생성된 클라이언트 ID 목록에서 방금 만든 항목 클릭
2. **"JSON 다운로드"** 클릭
3. 파일명을 `client_secret.json`으로 변경하여 작업 폴더에 저장

### 3.3 토큰 발급 스크립트

```python
#!/usr/bin/env python3
"""OAuth 2.0으로 ACCESS_TOKEN 발급 (개인 계정)"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]

def get_token():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        SCOPES
    )
    # 브라우저가 열리며 로그인 요청
    creds = flow.run_local_server(port=0)

    print("=" * 60)
    print("ACCESS_TOKEN:")
    print(creds.token)
    print("=" * 60)

    # 재사용을 위해 저장
    from google.oauth2.credentials import Credentials
    with open('token.json', 'w') as f:
        f.write(creds.to_json())

    print("\ntoken.json 저장 완료. 재실행 시 재로그인 불필요.")

if __name__ == '__main__':
    get_token()
```

### 3.4 실행 방법

```bash
# 라이브러리 설치
pip install google-auth google-auth-oauthlib

# 스크립트 실행
python get_oauth_token.py
```

1. 브라우저가 자동으로 열립니다
2. Google 계정으로 로그인합니다
3. **"허용"** 버튼을 클릭합니다
4. 터미널에 ACCESS_TOKEN이 출력됩니다
5. curl에 사용합니다:

```bash
curl -X GET \
  "https://www.googleapis.com/drive/v3/about?fields=user" \
  -H "Authorization: Bearer ya29.a0Ae...출력된_토큰..."
```

### 3.5 토큰 갱신

토큰이 만료되면(1시간) 저장된 `token.json`에서 리프레시 토큰으로 자동 갱신합니다:

```python
#!/usr/bin/env python3
"""저장된 token.json에서 ACCESS_TOKEN 갱신"""

import os
from google.oauth2.credentials import Credentials
import google.auth.transport.requests

def refresh_token():
    if not os.path.exists('token.json'):
        print("token.json이 없습니다. 먼저 get_oauth_token.py를 실행하세요.")
        return

    creds = Credentials.from_authorized_user_file('token.json',
        scopes=['https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'])

    if creds.expired and creds.refresh_token:
        creds.refresh(google.auth.transport.requests.Request())
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
        print("토큰 갱신 완료!")

    print("ACCESS_TOKEN:")
    print(creds.token)

if __name__ == '__main__':
    refresh_token()
```

---

## 빠른 비교표

| 방법 | 설정 시간 | 토큰 자동 갱신 | 추천 용도 |
|------|-----------|:-------------:|-----------|
| **방법 1: Playground** | 5분 | ❌ 직접 클릭 | 빠른 테스트 |
| **방법 2: Service Account** | 10분 | ✅ 자동 | 자동화, 서버, 스크립트 |
| **방법 3: OAuth Client ID** | 10분 | ✅ 자동 | 내 개인 계정 접근 |

> **추천**: 자동화가 목적이라면 **방법 2 (Service Account)**가 가장 편리합니다.
> 한번 설정하고 나면 `gcloud auth print-access-token` 한 줄로 토큰을 받을 수 있습니다.

---

## 유용한 curl 명령어 모음

### 내 Drive 정보 확인
```bash
curl -s "https://www.googleapis.com/drive/v3/about?fields=user" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
```

### Drive 파일 목록 조회
```bash
curl -s "https://www.googleapis.com/drive/v3/files?pageSize=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
```

### Spreadsheet 값 읽기
```bash
SPREADSHEET_ID="스프레드시트ID를_여기에"
curl -s "https://sheets.googleapis.com/v4/spreadsheets/$SPREADSHEET_ID/values/Sheet1" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
```

### Spreadsheet 값 쓰기
```bash
SPREADSHEET_ID="스프레드시트ID를_여기에"
curl -X PUT \
  "https://sheets.googleapis.com/v4/spreadsheets/$SPREADSHEET_ID/values/Sheet1!A1?valueInputOption=USER_ENTERED" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"values":[["테스트","데이터"]]}'
```

### Spreadsheet에 행 추가 (맨 아래에 추가)
```bash
SPREADSHEET_ID="스프레드시트ID를_여기에"
curl -X POST \
  "https://sheets.googleapis.com/v4/spreadsheets/$SPREADSHEET_ID/values/Sheet1:append?valueInputOption=USER_ENTERED" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"values":[["2026-04-26","삼성전자","60000","매수"]]}'
```

---

## 토큰 디버깅

### 토큰이 유효한지 확인
```bash
curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$ACCESS_TOKEN" | python3 -m json.tool
```

유효하면 이런 결과가 나옵니다:
```json
{
  "issued_to": "123456789012-xxx.apps.googleusercontent.com",
  "audience": "123456789012-xxx.apps.googleusercontent.com",
  "scope": "https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets",
  "expires_in": 3599,
  "email": "xxx@xxx.iam.gserviceaccount.com",
  "verified_email": true,
  "access_type": "service_account"
}
```

### 토큰 만료 시 에러
```json
{
  "error": {
    "code": 401,
    "message": "Request had invalid authentication credentials.",
    "status": "UNAUTHENTICATED"
  }
}
```
→ 새 토큰을 발급받으세요.

---

## 파일 구조 정리

### 방법 2 (Service Account) 기준:
```
my-project/
├── service-account.json   ← 서비스 계정 키 (절대 커밋 금지!)
├── get_token.py           ← 토큰 발급 스크립트
└── .gitignore
```

### .gitignore 내용:
```
# Google 인증 파일
service-account.json
client_secret.json
token.json
*.json
```

---

## 요약: 가장 빠른 시작 방법

```bash
# 1. gcloud 설치 (https://cloud.google.com/sdk/docs/install)
# 2. 서비스 계정 JSON 파일 다운로드
# 3. 아래 한 줄 실행
gcloud auth activate-service-account --key-file=./service-account.json

# 4. 토큰 받기
ACCESS_TOKEN=$(gcloud auth print-access-token)

# 5. curl 실행!
curl -s "https://www.googleapis.com/drive/v3/about?fields=user" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

이것이 **가장 간단한** 방법입니다. gcloud만 설치되어 있으면 3줄로 끝납니다.
