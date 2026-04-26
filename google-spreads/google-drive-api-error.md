# Google Drive/Sheets API 403 Forbidden 오류 해결 가이드

## 오류 현상

```
requests.exceptions.HTTPError: 403 Client Error: Forbidden for url:
https://sheets.googleapis.com/v4/spreadsheets/1t-4bblYFpFKW1d_aFALmZ0F_gXGQdIaZd22KnbOvBGM/values/Sheet1!A1:Z50
```

---

## 403 오류의 세 가지 원인

### 원인 1: 토큰 스코프에 Sheets API 권한이 없음 (가장 흔함)

`GOOGLE_ACCESS_TOKEN`을 발급받을 때 **`https://www.googleapis.com/auth/spreadsheets`** 스코프를 포함하지 않으면 403이 발생합니다.

**확인 방법:**

```bash
# 현재 토큰의 스코프 확인
curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$GOOGLE_ACCESS_TOKEN" | python -m json.tool
```

아래 스코프 중 하나가 포함되어 있어야 합니다:
- `https://www.googleapis.com/auth/spreadsheets` (읽기/쓰기)
- `https://www.googleapis.com/auth/spreadsheets.readonly` (읽기 전용)
- `https://www.googleapis.com/auth/drive` (Drive 전체 접근)

**해결: 올바른 스코프로 토큰 재발급**

#### 방법 A: gcloud CLI로 토큰 발급

```bash
# 1. gcloud 로그인
gcloud auth login

# 2. Sheets API 스코프 포함 토큰 발급
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/spreadsheets"

# 3. 발급된 토큰 확인
gcloud auth application-default print-access-token

# 4. 환경변수 설정
export GOOGLE_ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
```

#### 방법 B: OAuth 2.0 Playground에서 직접 발급

1. [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) 접속
2. "Step 1"에서 **Google Sheets API v4** 펼치기 → `https://www.googleapis.com/auth/spreadsheets` 선택
3. **"Authorize APIs"** 클릭 → 구글 계정 로그인 → 권한 허용
4. **"Exchange authorization code for tokens"** 클릭
5. **Access token** 복사 → 환경변수 설정

#### 방법 C: Python 스크립트로 OAuth2 인증 (권장 - 자동 갱신)

아래 `oauth2_auth.py` 파일을 참조하세요.

---

### 원인 2: 시트가 토큰 소유 계정에 공유되지 않음

토큰이 유효해도 **해당 구글 계정에 시트 공유 권한이 없으면** 403이 발생합니다.

**확인 방법:**

```bash
# 토큰이 가진 계정 정보 확인
curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$GOOGLE_ACCESS_TOKEN"
```

응답에서 `"email": "xxx@gmail.com"`을 확인합니다.

**해결:**

1. Google Sheets에서 해당 시트를 엽니다
2. 우측 상단 **"공유"** 버튼 클릭
3. 위 이메일 주소를 추가합니다
4. 권한: **"편집자"** (데이터 쓰기도 필요하면) 또는 **"뷰어"** (읽기만 필요하면)

---

### 원인 3: 토큰 만료

Google Access Token은 **기본적으로 1시간 후 만료**됩니다.

**확인 방법:**

```bash
# 토큰 만료 시간 확인
curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$GOOGLE_ACCESS_TOKEN" | grep expires_in
```

`expires_in`이 음수면 이미 만료됨.

**해결:** 토큰 재발급 또는 Refresh Token 사용 (아래 참조)

---

## 권장 해결책: OAuth2 자동 인증 스크립트

토큰 수동 갱신 대신 `google-auth-oauthlib`를 사용하면 자동으로 갱신됩니다.

### 1. 의존성 설치

```bash
pip install google-auth-oauthlib google-auth google-auth-httplib2 google-api-python-client
```

### 2. Google Cloud Console에서 OAuth2 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API & Services** → **Library** → **Google Sheets API** → **Enable**
4. **API & Services** → **OAuth consent screen** → **External** → 사용자 이메일 추가
5. **API & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**
   - Application type: **Desktop app**
   - 다운로드 → `client_secret.json`으로 저장

### 3. 인증 스크립트 (`oauth2_auth.py`)

```python
#!/usr/bin/env python3
"""OAuth2를 사용한 Google Sheets API 인증 (토큰 자동 갱신)."""

import os
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 사용하려는 API 스코프
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_credentials_oauth2() -> Credentials:
    """OAuth2 desktop flow로 credentials를 얻습니다.

    첫 실행시 브라우저가 열리고 인증 후,
    두번째부터는 저장된 token.json을 사용합니다.
    """
    creds = None
    token_path = "token.json"
    client_secret_path = "client_secret.json"

    # token.json이 있으면 기존 토큰 로드
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # 토큰이 없거나 만료되었거나 유효하지 않으면 재인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # 새로 발급된 토큰 저장
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


def get_credentials_service_account() -> ServiceAccountCredentials:
    """서비스 어카운트 JSON 키로 인증합니다.

    서비스 어카운트 이메일을 시트에 공유해야 합니다.
    """
    key_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY", "service_account.json")
    return ServiceAccountCredentials.from_service_account_file(
        key_path, scopes=SCOPES
    )


# --- 사용 예시 ---
if __name__ == "__main__":
    # 방법 1: OAuth2 데스크톱 인증
    creds = get_credentials_oauth2()
    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = "1t-4bblYFpFKW1d_aFALmZ0F_gXGQdIaZd22KnbOvBGM"
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range="Sheet1!A1:Z50")
        .execute()
    )

    rows = result.get("values", [])
    print(f"조회된 행 수: {len(rows)}")
    for row in rows:
        print(row)
```

---

## 빠른 진단 체크리스트

| 단계 | 명령어 | 정상 결과 |
|------|--------|-----------|
| 1. 토큰 유효 확인 | `curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$GOOGLE_ACCESS_TOKEN"` | JSON 응답 (200) |
| 2. 스코프 확인 | 위 응답에서 `"scope"` 필드 확인 | `spreadsheets` 포함 |
| 3. 계정 확인 | 위 응답에서 `"email"` 확인 | 시트 공유된 계정 |
| 4. 시트 공유 | Google Sheets에서 "공유" 확인 | 위 이메일이 편집자로 등록 |
| 5. 토큰 재발급 | `gcloud auth application-default login --scopes="https://www.googleapis.com/auth/spreadsheets"` | 새 토큰 발급 |

---

## 가장 빠른 해결 순서

```bash
# 1. 현재 토큰 상태 확인
curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$GOOGLE_ACCESS_TOKEN" | python -m json.tool

# 2. scope에 spreadsheets가 없다면 → 새 토큰 발급
#    gcloud 사용시:
gcloud auth login
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/spreadsheets"
export GOOGLE_ACCESS_TOKEN=$(gcloud auth application-default print-access-token)

# 3. 시트에 계정 공유 확인 → Google Sheets에서 해당 이메일을 편집자로 추가

# 4. 재시도
python google_sheets_api.py
```

---

## ⚠️ 서비스 계정을 썼는데도 403이 나는 경우 (핵심)

### 문제: 인증 방식 불일치

**시트에 서비스 계정 `drive-sheets-bot@my-drive-app-494502.iam.gserviceaccount.com`을 편집자로 추가했는데도 403이 발생하는 근본 원인:**

현재 코드(`google_sheets_api.py`)는 **OAuth2 Bearer 토큰 방식**으로 인증합니다:

```python
headers = {"Authorization": f"Bearer {token}"}
```

그런데 `GOOGLE_ACCESS_TOKEN` 환경변수에 넣은 토큰이 **서비스 계정 토큰이 아니라 개인 구글 계정(GwagDalF@gmail.com)의 OAuth 토큰**일 가능성이 높습니다.

**즉:**
- 시트에는 **서비스 계정**을 공유해 줬지만
- 코드에서 쓰는 토큰은 **개인 계정** 토큰 → 이 계정은 시트에 공유되지 않음 → 403

### 해결책: 두 가지 접근법 중 하나 선택

---

### 해결책 A: 서비스 계정 JSON 키 파일로 인증 (권장)

서비스 계정 키 파일(`service_account.json`)을 내려받아 직접 사용합니다. 토큰 만료 걱정 없고 자동 갱신됩니다.

#### 1단계: 서비스 계정 키 파일 다운로드

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. **IAM & Admin** → **Service Accounts** 선택
3. `drive-sheets-bot@my-drive-app-494502.iam.gserviceaccount.com` 클릭
4. **Keys** 탭 → **Add Key** → **Create new key** → **JSON** 선택
5. 다운로드된 JSON 파일을 `service_account.json`으로 프로젝트에 저장

#### 2단계: 서비스 계정 인증 코드 사용

`service_account_sheets.py` 파일을 생성합니다:

```python
#!/usr/bin/env python3
"""서비스 계정 JSON 키로 Google Sheets API 호출."""

import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_service():
    """서비스 계정 키로 Sheets API 서비스 객체를 반환합니다."""
    key_path = os.environ.get(
        "GOOGLE_SERVICE_ACCOUNT_KEY",
        "service_account.json",  # 기본값: 현재 디렉토리의 키 파일
    )

    if not os.path.exists(key_path):
        print(f"Error: 서비스 계정 키 파일을 찾을 수 없습니다: {key_path}")
        print("Google Cloud Console에서 JSON 키를 다운로드하세요.")
        sys.exit(1)

    creds = service_account.Credentials.from_service_account_file(
        key_path, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def read_sheet(spreadsheet_id: str, range_name: str = "Sheet1!A1:Z100") -> list:
    """시트 데이터를 읽습니다."""
    service = get_service()
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    return result.get("values", [])


def append_sheet(
    spreadsheet_id: str,
    range_name: str,
    values: list[list[str]],
) -> dict:
    """시트에 데이터를 추가합니다."""
    service = get_service()
    body = {"values": values}
    return (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )


if __name__ == "__main__":
    SPREADSHEET_ID = "1t-4bblYFpFKW1d_aFALmZ0F_gXGQdIaZd22KnbOvBGM"

    print("=== 시트 데이터 조회 ===")
    rows = read_sheet(SPREADSHEET_ID, "Sheet1!A1:Z50")
    if not rows:
        print("데이터가 없습니다.")
    else:
        for row in rows:
            print(row)
```

#### 3단계: 실행

```bash
# 의존성 설치
pip install google-api-python-client google-auth google-auth-httplib2

# 실행 (키 파일이 현재 디렉토리에 있으면 환경변수 불필요)
python service_account_sheets.py

# 또는 키 파일 경로 지정
GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/my-key.json python service_account_sheets.py
```

---

### 해결책 B: 기존 Bearer 토큰 방식 유지 (개인 계정 사용)

서비스 계정을 쓰지 않고, **개인 구글 계정 토큰**으로 계속 작업하려면:

#### 1단계: 시트를 개인 계정에 공유

Google Sheets에서 **"공유"** 버튼 → `GwagDalF@gmail.com` (또는 토큰 발급 계정의 이메일)을 편집자로 추가합니다.

#### 2단계: 올바른 스코프로 토큰 재발급

```bash
gcloud auth login
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive"
export GOOGLE_ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
```

#### 3단계: 재시도

```bash
python google_sheets_api.py
```

---

### 해결책 A vs B 비교

| 항목 | 해결책 A (서비스 계정) | 해결책 B (개인 계정 토큰) |
|------|----------------------|------------------------|
| 토큰 만료 | **없음** (자동 갱신) | 1시간마다 재발급 필요 |
| 보안 | JSON 키 파일 관리 필요 | 토큰 환경변수 관리 |
| 시트 공유 | 서비스 계정 이메일에 공유 | 개인 계정에 공유 |
| 권장场景 | 자동화/서버/백그라운드 작업 | 개발/테스트/수동 작업 |

**자동화 목적이라면 해결책 A(서비스 계정)를 강력히 권장합니다.**

---

### 추가 진단: 내가 어떤 계정으로 인증하고 있나?

```bash
# 현재 토큰의 계정 확인
curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$GOOGLE_ACCESS_TOKEN" | python -m json.tool
```

응답에서:
- `"email": "GwagDalF@gmail.com"` → 개인 계정 토큰 (해결책 B 필요)
- `"email": "drive-sheets-bot@..."` → 서비스 계정 토큰 (이미 올바르게 설정됨, 다른 원인 확인)

만약 서비스 계정 토큰인데도 403이면:
1. Google Cloud Console에서 **Sheets API가 Enable**인지 확인
2. 서비스 계정에 **Sheets API 사용 권한**이 있는지 확인 (IAM에서 `Service Account User` 역할)
