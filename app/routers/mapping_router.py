from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import mapping_store
from typing import Optional

router = APIRouter(prefix="/mappings", tags=["mapping"])

class MapReq(BaseModel):
    agent_id: str          # phone or uuid
    chat_id: int           # Telegram chat id
    role: str              # Chatter / Moderator / Admin
    persona_id: str
    delay_sec: int = 2

class MapUpdateReq(BaseModel):
    role: Optional[str] = None
    persona_id: Optional[str] = None
    delay_sec: Optional[int] = None

@router.post("")
def save_map(m: MapReq):
    """새 매핑 생성"""
    mapping_store.save_mapping(
        m.agent_id, m.chat_id, m.role, m.persona_id, m.delay_sec
    )
    return {"status": "ok"}

@router.get("")
def list_all():
    """모든 매핑 목록 조회"""
    return mapping_store._load(mapping_store.MAP_FILE)

@router.get("/{agent_id}")
def list_agent_mappings(agent_id: str):
    """특정 계정의 모든 매핑 조회"""
    all_mappings = mapping_store._load(mapping_store.MAP_FILE)
    agent_mappings = {}
    
    for key, value in all_mappings.items():
        if key.startswith(f"{agent_id}:"):
            chat_id = key.split(":")[1]
            agent_mappings[chat_id] = value
    
    return {
        "agent_id": agent_id,
        "mappings": agent_mappings
    }

@router.get("/{agent_id}/{chat_id}")
def get_mapping(agent_id: str, chat_id: int):
    """특정 채팅방 매핑 조회"""
    mapping = mapping_store.get_mapping(agent_id, chat_id)
    if not mapping:
        raise HTTPException(404, "매핑을 찾을 수 없습니다")
    return mapping

@router.put("/{agent_id}/{chat_id}")
def update_mapping(agent_id: str, chat_id: int, req: MapUpdateReq):
    """특정 채팅방 매핑 수정"""
    existing_mapping = mapping_store.get_mapping(agent_id, chat_id)
    if not existing_mapping:
        raise HTTPException(404, "매핑을 찾을 수 없습니다")
    
    # 기존 값과 새 값을 병합
    updated_role = req.role if req.role is not None else existing_mapping["role"]
    updated_persona_id = req.persona_id if req.persona_id is not None else existing_mapping["persona_id"]
    updated_delay = req.delay_sec if req.delay_sec is not None else existing_mapping["delay"]
    
    mapping_store.save_mapping(
        agent_id, chat_id, updated_role, updated_persona_id, updated_delay
    )
    return {"status": "ok"}

@router.delete("/{agent_id}/{chat_id}")
def delete_mapping(agent_id: str, chat_id: int):
    """특정 채팅방 매핑 삭제"""
    success = mapping_store.delete_mapping(agent_id, chat_id)
    if not success:
        raise HTTPException(404, "매핑을 찾을 수 없습니다")
    return {"status": "ok"}

@router.delete("/{agent_id}")
def delete_all_agent_mappings(agent_id: str):
    """특정 계정의 모든 매핑 삭제"""
    deleted_count = mapping_store.delete_agent_mappings(agent_id)
    return {"status": "ok", "deleted_count": deleted_count} 