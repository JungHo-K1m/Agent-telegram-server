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
│  └─ mapping_router.py   # 채팅방 매핑
├─ services/
│  ├─ telegram_service.py # 텔레그램 API
│  ├─ mapping_store.py    # JSON 기반 데이터 저장
│  └─ openai_service.py   # OpenAI API
├─ main.py                # FastAPI 앱
└─ worker.py              # 텔레그램 워커

data/
├─ agent_sessions.json    # 에이전트 세션 정보
├─ memberships.json       # 채팅방 매핑 정보
└─ personas.json          # 페르소나 정보
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
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
```

### 3. 서버 실행
```bash
# FastAPI 서버
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 워커 (별도 터미널)
python worker.py
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

## 🔄 사용 플로우

1. **인증**: `/auth` API로 텔레그램 세션 생성
2. **세션 저장**: `data/agent_sessions.json`에 세션 정보 추가
3. **페르소나 생성**: `/personas` API로 AI 페르소나 등록
4. **매핑 설정**: `/mappings` API로 채팅방과 페르소나 연결
5. **워커 실행**: `python worker.py`로 자동 응답 시작

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