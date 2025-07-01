from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import account_service
from typing import Optional

router = APIRouter(prefix="/accounts", tags=["account"])

class AccountCreateReq(BaseModel):
    tenant_id: str
    account_id: str
    name: str
    api_id: int
    api_hash: str
    phone_number: str

class AccountUpdateReq(BaseModel):
    tenant_id: str
    name: Optional[str] = None
    api_id: Optional[int] = None
    api_hash: Optional[str] = None
    phone_number: Optional[str] = None

@router.post("")
def create_account(req: AccountCreateReq):
    """새 계정 생성"""
    account_service.add_account(
        req.tenant_id, req.account_id, req.name, req.api_id, req.api_hash, req.phone_number
    )
    return {"status": "ok", "account_id": req.account_id}

@router.get("")
def list_accounts(tenant_id: str):
    """모든 계정 목록 조회"""
    return account_service.list_accounts(tenant_id)

@router.get("/{account_id}")
def get_account(account_id: str, tenant_id: str):
    """특정 계정 정보 조회"""
    account = account_service.get_account(tenant_id, account_id)
    if not account:
        raise HTTPException(404, "계정을 찾을 수 없습니다")
    return account

@router.put("/{account_id}")
def update_account(account_id: str, req: AccountUpdateReq):
    """계정 정보 업데이트"""
    account_service.update_account(
        req.tenant_id, account_id, req.name, req.api_id, req.api_hash, req.phone_number
    )
    return {"status": "ok"}

@router.delete("/{account_id}")
def delete_account(account_id: str, tenant_id: str):
    """계정 삭제"""
    account_service.delete_account(tenant_id, account_id)
    return {"status": "ok"} 