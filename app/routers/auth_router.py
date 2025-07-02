from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import uuid

from app.services import telegram_service, supabase_service
from utils.logging import log

router = APIRouter(prefix="/auth", tags=["auth"])

# 1) 모든 필드 '필수' 로 변경
class StartReq(BaseModel):
    tenant_id: str
    agent_id: str  # 에이전트 ID로 변경
    phone_number: str

class CodeReq(BaseModel):
    api_id: int
    api_hash: str
    phone_number: str

class VerifyReq(BaseModel):
    auth_id: str
    code: str
    password: str | None = None

class SessionReq(BaseModel):
    tenant_id: str
    agent_id: str

_pending: dict[str, telegram_service.TelegramClient] = {}

@router.options("/start")
async def options_start():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.post("/start")
async def start_auth(req: StartReq):
    # 에이전트 정보 조회
    agent = supabase_service.get_agent(req.tenant_id, req.agent_id)
    if not agent:
        raise HTTPException(404, "에이전트를 찾을 수 없습니다")
    
    # 전화번호 확인 (요청된 번호가 있으면 사용, 없으면 에이전트에 저장된 번호 사용)
    phone_number = req.phone_number if req.phone_number else agent["phone_number"]
    
    try:
        client = await telegram_service.send_code(agent["api_id"], agent["api_hash"], phone_number)
    except Exception as e:
        raise HTTPException(400, f"코드 발송 실패: {e}")

    auth_id = str(uuid.uuid4())
    _pending[auth_id] = client
    log.info("code_sent", auth_id=auth_id, agent_id=req.agent_id, phone=phone_number)
    return {"auth_id": auth_id, "phase": "waiting_code", "agent_id": req.agent_id}

@router.options("/code")
async def options_code():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.post("/code")
async def send_code(req: CodeReq):
    """
    직접 제공된 api_id, api_hash, phone_number로 인증코드를 발송합니다.
    """
    try:
        client = await telegram_service.send_code(req.api_id, req.api_hash, req.phone_number)
    except Exception as e:
        raise HTTPException(400, f"코드 발송 실패: {e}")

    auth_id = str(uuid.uuid4())
    _pending[auth_id] = client
    log.info("code_sent", auth_id=auth_id, phone=req.phone_number, api_id=req.api_id)
    return {"auth_id": auth_id, "phase": "waiting_code", "message": "인증코드가 발송되었습니다"}

@router.options("/verify")
async def options_verify():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.post("/verify")
async def verify_code(req: VerifyReq):
    client = _pending.pop(req.auth_id, None)
    if not client:
        raise HTTPException(404, "인증 세션이 없습니다")

    try:
        session_str = await telegram_service.sign_in(
            client, phone=client._phone, code=req.code, password=req.password
        )
        
        # Supabase에 세션 저장
        agent_id = client._phone
        supabase_service.save_agent_session(agent_id, session_str)
        
    except Exception as e:
        raise HTTPException(401, f"인증 실패: {e}")

    log.info("auth_success", auth_id=req.auth_id)
    return {"session_string": session_str}

@router.options("/session")
async def options_session():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.post("/session")
async def get_session(req: SessionReq):
    """
    특정 에이전트의 세션 스트링을 조회합니다.
    """
    session_info = supabase_service.get_agent_session_with_tenant(req.tenant_id, req.agent_id)
    if not session_info:
        raise HTTPException(404, "에이전트를 찾을 수 없거나 활성 세션이 없습니다")
    
    if not session_info["is_active"]:
        raise HTTPException(404, "활성 세션이 없습니다")
    
    log.info("session_retrieved", tenant_id=req.tenant_id, agent_id=req.agent_id)
    return {
        "agent_id": session_info["agent_id"],
        "phone_number": session_info["phone_number"],
        "session_string": session_info["session_string"],
        "is_active": session_info["is_active"],
        "created_at": session_info["created_at"]
    }

@router.options("/sessions")
async def options_sessions():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.get("/sessions/{tenant_id}")
async def list_sessions(tenant_id: str):
    """
    테넌트의 모든 에이전트 세션을 조회합니다.
    """
    sessions = supabase_service.list_tenant_sessions(tenant_id)
    
    log.info("sessions_listed", tenant_id=tenant_id, count=len(sessions))
    return {
        "tenant_id": tenant_id,
        "sessions": sessions,
        "total_count": len(sessions)
    }
