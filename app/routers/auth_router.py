from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import uuid

from app.services import telegram_service, account_service
from utils.logging import log

router = APIRouter(prefix="/auth", tags=["auth"])

# 1) 모든 필드 '필수' 로 변경
class StartReq(BaseModel):
    account_id: str  # 계정 ID로 변경
    phone_number: str  # 선택사항 (계정에 저장된 번호와 다를 경우)

class VerifyReq(BaseModel):
    auth_id: str
    code: str
    password: str | None = None

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
    # 계정 정보 조회
    account = account_service.get_account(req.account_id)
    if not account:
        raise HTTPException(404, "계정을 찾을 수 없습니다")
    
    # 전화번호 확인 (요청된 번호가 있으면 사용, 없으면 계정에 저장된 번호 사용)
    phone_number = req.phone_number if req.phone_number else account["phone_number"]
    
    try:
        client = await telegram_service.send_code(account["api_id"], account["api_hash"], phone_number)
    except Exception as e:
        raise HTTPException(400, f"코드 발송 실패: {e}")

    auth_id = str(uuid.uuid4())
    _pending[auth_id] = client
    log.info("code_sent", auth_id=auth_id, account_id=req.account_id, phone=phone_number)
    return {"auth_id": auth_id, "phase": "waiting_code", "account_id": req.account_id}

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
    except Exception as e:
        raise HTTPException(401, f"인증 실패: {e}")

    log.info("auth_success", auth_id=req.auth_id)
    return {"session_string": session_str}
