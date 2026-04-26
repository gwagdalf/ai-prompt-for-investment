# Google Drive API 서비스 계정 403 오류 해결 가이드

## 오류 현상

```
requests.exceptions.HTTPError: 403 Client Error: Forbidden for url:
https://www.googleapis.com/drive/v3/about?fields=user
```

## 문제 원인

**서비스 계정 토큰 + Bearer 인증 방식의 근본적 불일치**

`gcloud auth activate-service-account --key-file=...`로 로그인한 후 `gcloud auth application-default print-access-token`으로 발급받은 토큰은 **서비스 계정용이 아니라 사용자 계정용 OAuth2 토큰 형식**입니다. 이 토큰을 Drive API에 Bearer로 전달해도 서비스 계정의 identity를 제대로 전달하지 못해 403이 발생합니다.

서비스 계정은 **JWT-based 인증**을 사용해야 하며, 단순 Bearer 토큰으로 동작하지 않습니다.

---

## 해결책: google-auth 라이브러리로 서비스 계정 인증

### 1단계: 의존성 설치

```bash
pip install google-api-python-client google-auth google-auth-httplib2
```

### 2단계: drive_user_info.py 수정

`requests` + Bearer 토큰 대신 `google-api-python-client`의 서비스 계정 인증을 사용합니다.

```python
#!/usr/bin/env python3
"""서비스 계정 JSON 키로 Google Drive API - 현재 사용자 정보 조회."""

import json
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_current_user():
    """서비스 계정 키로 Drive API /about 엔드포인트를 호출합니다."""
    key_path = os.environ.get(
        "GOOGLE_SERVICE_ACCOUNT_KEY",
        r"C:\git\credential\google\my-drive-app-494502-5b91968ecfad.json",
    )

    if not os.path.exists(key_path):
        print(f"Error: 서비스 계정 키 파일을 찾을 수 없습니다: {key_path}")
        sys.exit(1)

    # 서비스 계정 인증 (JWT 기반, 토큰 자동 갱신)
    creds = service_account.Credentials.from_service_account_file(
        key_path, scopes=SCOPES
    )

    # Drive API v3 서비스 객체 생성
    service = build("drive", "v3", credentials=creds)

    # /about 엔드포인트 호출
    result = service.about().get(fields="user").execute()
    return result


if __name__ == "__main__":
    result = get_current_user()
    user = result.get("user", {})

    print("=== Drive API 인증 계정 정보 ===")
    print(f"이름: {user.get('displayName')}")
    print(f"이메일: {user.get('emailAddress')}")
    print(f"종류: {user.get('kind')}")
    print(f"권한 ID: {user.get('permissionId')}")
    print(f"\n전체 응답:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 3단계: 실행

```bash
# 키 파일 경로가 기본값이면 그대로 실행
python drive_user_info.py

# 또는 환경변수로 경로 지정
$env:GOOGLE_SERVICE_ACCOUNT_KEY="C:\git\credential\google\my-drive-app-494502-5b91968ecfad.json"
python drive_user_info.py
```

### 예상 응답

```
=== Drive API 인증 계정 정보 ===
이름: drive-sheets-bot
이메일: drive-sheets-bot@my-drive-app-494502.iam.gserviceaccount.com
종류: drive#user
권한 ID: 12345678901234567890

전체 응답:
{
  "user": {
    "displayName": "drive-sheets-bot",
    "emailAddress": "drive-sheets-bot@my-drive-app-494502.iam.gserviceaccount.com",
    "kind": "drive#user",
    "permissionId": "12345678901234567890"
  }
}
```

---

## 왜 gcloud Bearer 토큰으로는 안 되는가?

| 항목 | gcloud Bearer 토큰 | google-auth 서비스 계정 |
|------|-------------------|------------------------|
| 인증 방식 | OAuth2 Access Token | JWT → Access Token 자동 변환 |
| Identity | 사용자 컨텍스트 | 서비스 계정 이메일 |
| 토큰 갱신 | 수동 (1시간 만료) | **자동** |
| Drive API 동작 | ❌ 403 Forbidden | ✅ 정상 |

`gcloud auth activate-service-account`는 gcloud CLI 도구 자체의 인증을 위한 것이며, 이를 통해 발급받은 토큰을 외부 Python 코드에서 Bearer로 쓰면 서비스 계정의 identity가 손실됩니다.

`google-auth` 라이브러리는 서비스 계정 JSON 키의 private key로 **JWT를 서명**하고, Google OAuth2 서버에서 이를 검증해 실제 Access Token으로 교환합니다. 이 과정에서 서비스 계정 이메일이 identity로 올바르게 전달됩니다.

---

## 체크리스트: 그래도 안 된다면

1. **Google Cloud Console에서 Drive API 활성화 확인**
   - [API Library](https://console.cloud.google.com/apis/library) → **Google Drive API** → **Enable**

2. **서비스 계정에 IAM 역할 확인**
   - [IAM](https://console.cloud.google.com/iam-admin/iam) → `drive-sheets-bot` → 역할에 **Viewer** 이상 있는지 확인

3. **시트 공유 확인** (Sheets API 호출시)
   - `drive-sheets-bot@my-drive-app-494502.iam.gserviceaccount.com`이 시트 편집자로 등록되었는지 확인

---

## curl로 서비스 계정 인증하는 방법 (참고)

curl에서도 서비스 계정 인증을 하려면 JWT를 직접 서명해야 하므로 복잡합니다. 대신 `gcloud auth print-access-token`이 아닌 아래 방법을 사용하세요:

```bash
# 1. 서비스 계정으로 ADC 설정
set GOOGLE_APPLICATION_CREDENTIALS=C:\git\credential\google\my-drive-app-494502-5b91968ecfad.json

# 2. ADC 토큰 발급 (서비스 계정용)
gcloud auth application-default login  # 이건 사용자 인증이므로 서비스 계정에는 부적합

# 대신 Python google-auth를 사용하는 것이 가장 간단합니다
```

결론: **curl + Bearer 토큰은 개인 계정에 적합, 서비스 계정에는 Python google-auth 라이브러리를 사용하세요.**
