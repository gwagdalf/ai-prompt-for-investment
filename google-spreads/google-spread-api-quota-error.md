# Google Sheets API Quota Error 해결 가이드

## 오류 분석

```
HttpError 429: Quota exceeded for quota metric 'Read requests'
limit 'Read requests per minute per user' of service 'sheets.googleapis.com'
for consumer 'project_number:868560227879'
```

| 항목 | 값 |
|------|------|
| **쿼타 메트릭** | `sheets.googleapis.com/read_requests` |
| **현재 한도** | **60회/분/사용자** |
| **대상 프로젝트** | `project_number:868560227879` |
| **적용 범위** | Global (전 리전 공통) |

## 해결 방법 4가지

### 방법 1: Google Cloud Console에서 쿼타 증량 신청 (권장)

1. **Google Cloud Console** 접속: <https://cloud.google.com/docs/quotas/help/request_increase>
2. 또는 직접 링크: <https://console.cloud.google.com/apis/api/sheets.googleapis.com/quotas>
3. 프로젝트 `my-drive-app-494502` (project_number: 868560227879) 선택
4. **ReadRequestsPerMinutePerUser** 쿼타 찾기
5. **할당량 수정(펜실 아이콘)** 클릭
6. 새로운 한도 요청 (예: 600/분)
7. 신청 사유 작성 후 제출

**처리 시간**: 보통 1~2 영업일 내에 승인됨

---

### 방법 2: 코드에서 호출 횟수 줄이기 (즉시 적용 가능)

#### 2-1. Batch API 사용

여러 시트 데이터를 한 번의 API 호출로 가져올 수 있습니다:

```python
# 기존: 각 시트마다 별도 호출 (31개 시트 = 31회)
for sheet_name in sheets:
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A2:L100"
    ).execute()

# 개선: spreadsheets().batchGet()으로 한 번에 호출
ranges = [f"{name}!A2:L100" for name in target_sheets]
result = (
    service.spreadsheets()
    .values()
    .batchGet(spreadsheetId=spreadsheet_id, ranges=ranges)
    .execute()
)
# result['valueRanges']에 각 시트 데이터가 순서대로 들어옴
```

#### 2-2. spreadsheets().get()으로 전체 데이터 한 번에 가져오기

```python
# 시트 메타데이터 + 모든 시트 데이터를 한 번의 호출로 가져옴
result = (
    service.spreadsheets()
    .get(
        spreadsheetId=spreadsheet_id,
        ranges=["Sheet1", "Sheet2"],  # 가져올 시트 목록
        includeGridData=True,         # 실제 셀 데이터 포함
    )
    .execute()
)
```

#### 2-3. API 호출 간 지연 (Retry with backoff)

```python
import time
from googleapiclient.errors import HttpError

def call_with_retry(func, max_retries=5, base_delay=1):
    """지수 백오프로 API 호출 재시도"""
    for attempt in range(max_retries):
        try:
            return func()
        except HttpError as e:
            if e.resp.status == 429:
                wait = base_delay * (2 ** attempt)  # 1, 2, 4, 8, 16초
                print(f"Quota 초과 ({attempt+1}/{max_retries}) - {wait}초 대기")
                time.sleep(wait)
            else:
                raise
    raise Exception("최대 재시도 횟수 초과")
```

---

### 방법 3: 서비스 계정 여러 개 사용

여러 서비스 계정을 번갈아 사용하면 사용자별 쿼타를 분산할 수 있습니다:

```python
SERVICE_ACCOUNTS = [
    "account1.json",
    "account2.json", 
    "account3.json",
]

def get_round_robin_credentials(index):
    key_path = SERVICE_ACCOUNTS[index % len(SERVICE_ACCOUNTS)]
    return service_account.Credentials.from_service_account_file(
        key_path, scopes=SCOPES
    )
```

---

### 방법 4: Google Workspace 관리자라면

프로젝트가 Google Workspace 조직에 속해 있다면, **관리 콘솔에서 API 액세스 수준**을 조정할 수 있습니다. 개인 프로젝트라면 방법 1을 사용해야 합니다.

---

## 권장 전략

| 상황 | 해결책 |
|------|--------|
| 즉시 해결 필요 | 방법 2 (코드 최적화) |
| 지속적인 사용 | 방법 1 (쿼타 증량) |
| 대량 배치 작업 | 방법 2 + 방법 3 조합 |

**현재 프로젝트에서는 방법 1 + 방법 2를 함께 적용하는 것을 권장합니다.**
