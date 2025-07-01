from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import supabase_service
from typing import Optional

router = APIRouter(prefix="/mappings", tags=["mapping"])

class MapReq(BaseModel):
    tenant_id: str
    agent_id: str          # phone or uuid
    chat_id: int           # Telegram chat id
    role: str              # Chatter / Moderator / Admin
    persona_id: str
    delay_sec: int = 2

class MapUpdateReq(BaseModel):
    tenant_id: str
    role: Optional[str] = None
    persona_id: Optional[str] = None
    delay_sec: Optional[int] = None

@router.post("")
def save_map(m: MapReq):
    """새 매핑 생성"""
    supabase_service.save_mapping(
        m.tenant_id, m.agent_id, m.chat_id, m.role, m.persona_id, m.delay_sec
    )
    return {"status": "ok"}

@router.get("")
def list_all(tenant_id: str):
    """모든 매핑 목록 조회"""
    return supabase_service.list_all_mappings(tenant_id)

@router.get("/{agent_id}")
def list_agent_mappings(agent_id: str, tenant_id: str):
    """특정 계정의 모든 매핑 조회"""
    mappings = supabase_service.list_agent_mappings(tenant_id, agent_id)
    return {
        "agent_id": agent_id,
        "mappings": mappings
    }

@router.get("/{agent_id}/{chat_id}")
def get_mapping(agent_id: str, chat_id: int, tenant_id: str):
    """특정 채팅방 매핑 조회"""
    mapping = supabase_service.get_mapping(tenant_id, agent_id, chat_id)
    if not mapping:
        raise HTTPException(404, "매핑을 찾을 수 없습니다")
    return mapping

@router.put("/{agent_id}/{chat_id}")
def update_mapping(agent_id: str, chat_id: int, req: MapUpdateReq):
    """특정 채팅방 매핑 수정"""
    existing_mapping = supabase_service.get_mapping(req.tenant_id, agent_id, chat_id)
    if not existing_mapping:
        raise HTTPException(404, "매핑을 찾을 수 없습니다")
    
    # 업데이트할 필드만 준비
    update_data = {}
    if req.role is not None:
        update_data["role"] = req.role
    if req.persona_id is not None:
        update_data["persona_id"] = req.persona_id
    if req.delay_sec is not None:
        update_data["delay_sec"] = req.delay_sec
    
    success = supabase_service.update_mapping(req.tenant_id, agent_id, chat_id, **update_data)
    if not success:
        raise HTTPException(500, "매핑 업데이트에 실패했습니다")
    
    return {"status": "ok"}

@router.delete("/{agent_id}/{chat_id}")
def delete_mapping(agent_id: str, chat_id: int, tenant_id: str):
    """특정 채팅방 매핑 삭제"""
    success = supabase_service.delete_mapping(tenant_id, agent_id, chat_id)
    if not success:
        raise HTTPException(404, "매핑을 찾을 수 없습니다")
    return {"status": "ok"}

@router.delete("/{agent_id}")
def delete_all_agent_mappings(agent_id: str, tenant_id: str):
    """특정 계정의 모든 매핑 삭제"""
    deleted_count = supabase_service.delete_agent_mappings(tenant_id, agent_id)
    return {"status": "ok", "deleted_count": deleted_count} 