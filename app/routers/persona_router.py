from fastapi import APIRouter
from pydantic import BaseModel
from app.services import supabase_service

router = APIRouter(prefix="/personas", tags=["persona"])

class PersonaReq(BaseModel):
    name: str
    system_prompt: str

@router.post("")
def create_persona(p: PersonaReq):
    pid = supabase_service.add_persona(p.name, p.system_prompt)
    return {"persona_id": pid}

@router.get("")
def list_personas():
    return supabase_service.list_personas() 