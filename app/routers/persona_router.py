from fastapi import APIRouter
from pydantic import BaseModel
from app.services import mapping_store

router = APIRouter(prefix="/personas", tags=["persona"])

class PersonaReq(BaseModel):
    name: str
    system_prompt: str

@router.post("")
def create_persona(p: PersonaReq):
    pid = mapping_store.add_persona(p.name, p.system_prompt)
    return {"persona_id": pid}

@router.get("")
def list_personas():
    return mapping_store.list_personas() 