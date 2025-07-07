# Telegram AI Agent Hub

텔레그램 채팅방에서 OpenAI 기반 자동 응답을 제공하는 AI 에이전트 시스템입니다.

## 🚀 기능

- **텔레그램 인증**: API를 통한 세션 생성
- **페르소나 관리**: 다양한 AI 페르소나 생성 및 관리
- **채팅방 매핑**: 채팅방별 롤과 페르소나 설정
- **자동 응답**: OpenAI GPT를 활용한 지능형 자동 응답

## 📁 프로젝트 구조

```
app/
├─ routers/
│  ├─ auth_router.py      # 텔레그램 인증
│  ├─ persona_router.py   # 페르소나 관리
│  ├─ mapping_router.py   # 채팅방 매핑
│  ├─ agent_router.py     # 에이전트 관리
│  └─ worker_router.py    # 워커 관리
├─ services/
│  ├─ telegram_service.py # 텔레그램 API
│  ├─ openai_service.py   # OpenAI API
│  ├─ supabase_service.py # Supabase 데이터베이스
│  ├─ agent_service.py    # 에이전트 서비스
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
POST /auth/start
{
  "api_id": 123456,
  "api_hash": "your_api_hash",
  "phone_number": "+82123456789"
}

# 인증 코드 확인
POST /auth/verify
{
  "auth_id": "uuid",
  "code": "123456",
  "password": "2fa_password"  # 선택사항
}
```

### 2. 페르소나 생성

```bash
POST /personas
{
  "name": "친근한 챗봇",
  "system_prompt": "당신은 친근하고 도움이 되는 AI 어시스턴트입니다."
}
```

### 3. 채팅방 매핑

```bash
POST /mappings
{
  "agent_id": "+82123456789",
  "chat_id": -1001234567890,
  "role": "Chatter",
  "persona_id": "uuid",
  "delay_sec": 3
}
```

### 4. 워커 관리

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

1. **재단 생성**: 대시보드에서 재단 정보 등록
2. **페르소나 생성**: 대시보드에서 AI 페르소나 등록
3. **에이전트 등록**: 대시보드에서 텔레그램 계정 인증 및 등록
4. **매핑 설정**: 대시보드에서 채팅방과 페르소나 연결
5. **워커 실행**: `python worker_improved.py`로 자동 응답 시작

## 🎯 롤 타입

- **Chatter**: 친근한 대화 상대
- **Moderator**: 엄격하지만 정중한 관리자
- **Admin**: 시스템 관리자 봇

## 🔧 확장 가능성

- **데이터베이스**: JSON → Supabase/PostgreSQL
- **캐싱**: 메모리 → Redis
- **모니터링**: 토큰 사용량 추적
- **멀티 모델**: GPT-4, Claude 등 다양한 AI 모델 지원

## 📝 라이선스

MIT License
