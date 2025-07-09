from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import uuid

from app.services import telegram_service, supabase_service
from utils.logging import log

router = APIRouter(prefix="/auth", tags=["auth"])

class CodeReq(BaseModel):
    api_id: int
    api_hash: str
    phone_number: str

class SessionStringReq(BaseModel):
    auth_id: str
    code: str
    password: str | None = None

_pending: dict[str, dict] = {}

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
    _pending[auth_id] = {
        "client": client,
        "api_id": req.api_id,
        "api_hash": req.api_hash,
        "phone_number": req.phone_number
    }
    log.info("code_sent", auth_id=auth_id, phone=req.phone_number, api_id=req.api_id)
    return {"auth_id": auth_id, "phase": "waiting_code", "message": "인증코드가 발송되었습니다"}

@router.options("/session-string")
async def options_session_string():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.post("/session-string")
async def get_session_string(req: SessionStringReq):
    """
    auth_id, code, password만 받아서 세션 스트링을 반환합니다.
    """
    pending = _pending.pop(req.auth_id, None)
    if not pending:
        raise HTTPException(404, "인증 세션이 없습니다. 인증코드를 먼저 요청하세요.")
    
    client = pending["client"]
    try:
        session_str = await telegram_service.sign_in(
            client,
            phone=pending["phone_number"],
            code=req.code,
            password=req.password
        )
        await client.disconnect()
        return {"session_string": session_str}
    except Exception as e:
        raise HTTPException(400, f"세션 스트링 획득 실패: {e}")
