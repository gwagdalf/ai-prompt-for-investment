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
    """서비스 계정 키로 Drive API /about 엔드포인트를 호출합니다.

    Returns:
        tuple: (user_info_dict, credentials)
    """
    # 키 파일 경로: project root의 1단계 상위 디렉토리
    # project root(ai-prompt-for-investment/)의 1단계 상위 = ../../../../
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_key_path = os.path.join(base_dir, "..", "..", "..", "google-service-account.json")

    key_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY", default_key_path)

    if not os.path.exists(key_path):
        print(f"Error: 서비스 계정 키 파일을 찾을 수 없습니다: {key_path}")
        print("GOOGLE_SERVICE_ACCOUNT_KEY 환경변수로 경로를 지정하세요.")
        sys.exit(1)

    creds = service_account.Credentials.from_service_account_file(
        key_path, scopes=SCOPES
    )

    service = build("drive", "v3", credentials=creds)
    result = service.about().get(fields="user").execute()
    return result, creds


if __name__ == "__main__":
    result, _ = get_current_user()
    user = result.get("user", {})

    print("=== Drive API 인증 계정 정보 ===")
    print(f"이름: {user.get('displayName')}")
    print(f"이메일: {user.get('emailAddress')}")
    print(f"종류: {user.get('kind')}")
    print(f"권한 ID: {user.get('permissionId')}")
    print(f"\n전체 응답:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
