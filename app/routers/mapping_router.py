from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import mapping_store

router = APIRouter(prefix="/mappings", tags=["mapping"])

class MapReq(BaseModel):
    agent_id: str          # phone or uuid
    chat_id: int           # Telegram chat id
    role: str              # Chatter / Moderator / Admin
    persona_id: str
    delay_sec: int = 2

@router.post("")
def save_map(m: MapReq):
    mapping_store.save_mapping(
        m.agent_id, m.chat_id, m.role, m.persona_id, m.delay_sec
    )
    return {"status": "ok"}

@router.get("")
def list_all():
    return mapping_store._load(mapping_store.MAP_FILE) 