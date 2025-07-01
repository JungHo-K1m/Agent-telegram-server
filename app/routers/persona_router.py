from fastapi import APIRouter
from pydantic import BaseModel
from app.services import supabase_service

router = APIRouter(prefix="/personas", tags=["persona"])

class PersonaReq(BaseModel):
    tenant_id: str
    name: str
    system_prompt: str

@router.post("")
def create_persona(p: PersonaReq):
    pid = supabase_service.add_persona(p.tenant_id, p.name, p.system_prompt)
    return {"persona_id": pid}

@router.get("")
def list_personas(tenant_id: str):
    return supabase_service.list_personas(tenant_id) 