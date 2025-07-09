# Telegram AI Agent Hub

텔레그램 채팅방에서 OpenAI 기반 자동 응답을 제공하는 AI 에이전트 시스템입니다.

## 🚀 기능

- **텔레그램 인증**: API를 통한 세션 생성
- **실시간 AI 응답**: OpenAI GPT를 활용한 지능형 자동 응답
- **다중 테넌트 지원**: 각 재단별 독립적인 에이전트 관리
- **워커 관리**: 실시간 에이전트 상태 모니터링 및 제어

## 📁 프로젝트 구조

```
app/
├─ routers/
│  ├─ auth_router.py      # 텔레그램 인증
│  └─ worker_router.py    # 워커 관리
├─ services/
│  ├─ telegram_service.py # 텔레그램 API
│  ├─ openai_service.py   # OpenAI API
│  ├─ supabase_service.py # Supabase 데이터베이스
│  └─ worker_service.py   # 워커 서비스
├─ main.py                # FastAPI 앱
└─ config.py              # 설정 관리
├─ worker_improved.py     # 개선된 워커 스크립트
└─ utils/
    └─ logging.py         # 로깅 설정
```

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# .env 파일 생성
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_key
```

### 3. 서버 실행

```bash
# FastAPI 서버
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 워커 (별도 터미널)
python worker_improved.py
```

## 📡 API 사용법

### 1. 텔레그램 인증

```bash
# 인증 코드 발송
POST /auth/code
{
  "api_id": 123456,
  "api_hash": "your_api_hash",
  "phone_number": "+82123456789"
}

# 세션 스트링 획득
POST /auth/session-string
{
  "auth_id": "uuid",
  "code": "123456",
  "password": "2fa_password"  # 선택사항
}
```

### 2. 워커 관리

```bash
# 워커 상태 조회
GET /worker/status

# 워커 시작
POST /worker/start

# 워커에 에이전트 추가
POST /worker/add-agent
{
  "tenant_id": "tenant-uuid",
  "agent_id": "agent-uuid"
}
```

## 🔄 사용 플로우

1. **대시보드에서 관리**: 재단, 페르소나, 에이전트, 매핑 등 모든 데이터는 대시보드에서 관리
2. **텔레그램 인증**: `/auth/code`와 `/auth/session-string` API를 통한 인증
3. **워커 실행**: `python worker_improved.py`로 자동 응답 시작
4. **워커 관리**: `/worker/*` API를 통한 워커 상태 모니터링 및 제어

## 🎯 주요 특징

- **다중 테넌트**: 각 재단별 독립적인 에이전트 관리
- **실시간 처리**: 텔레그램 메시지 즉시 감지 및 응답
- **컨텍스트 유지**: 대화 연속성을 위한 메시지 캐싱
- **확장 가능**: 동적 에이전트 추가/제거 지원

## 🔧 확장 가능성

- **데이터베이스**: JSON → Supabase/PostgreSQL
- **캐싱**: 메모리 → Redis
- **모니터링**: 토큰 사용량 추적
- **멀티 모델**: GPT-4, Claude 등 다양한 AI 모델 지원

## 📝 라이선스

MIT License
