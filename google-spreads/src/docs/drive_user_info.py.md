# drive_user_info.py

Google Drive API 인증 및 현재 사용자 정보 조회 모듈입니다.

## 개요

서비스 계정(JSON 키 파일)을 사용하여 Google Drive API에 인증하고, `about().get()` 엔드포인트를 통해 현재 사용자 정보를 조회합니다. 다른 스크립트들이 공통으로 사용하는 인증 함수를 제공합니다.

## 주요 함수

### `get_current_user()`

서비스 계정 키 파일로 Drive API 인증 후 사용자 정보를 반환합니다.

- **반환값**: `tuple` — `(user_info_dict, credentials)`
- **키 파일 경로**: 프로젝트 루트의 `../../google-service-account.json` 또는 `GOOGLE_SERVICE_ACCOUNT_KEY` 환경변수

## 의존성

- `google.oauth2.service_account`
- `googleapiclient.discovery`

## 사용 예

```python
from drive_user_info import get_current_user

user_info, credentials = get_current_user()
user = user_info.get("user", {})
print(f"이름: {user.get('displayName')}")
print(f"이메일: {user.get('emailAddress')}")
```
