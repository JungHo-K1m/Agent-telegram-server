from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import agent_service
from typing import Optional

router = APIRouter(prefix="/agents", tags=["agent"])

class AgentCreateReq(BaseModel):
    tenant_id: str
    name: str
    api_id: int
    api_hash: str
    phone_number: str

class AgentUpdateReq(BaseModel):
    tenant_id: str
    name: Optional[str] = None
    api_id: Optional[int] = None
    api_hash: Optional[str] = None
    phone_number: Optional[str] = None

@router.post("")
def create_agent(req: AgentCreateReq):
    """새 에이전트 생성"""
    agent_service.add_agent(
        req.tenant_id, req.name, req.api_id, req.api_hash, req.phone_number
    )
    return {"status": "ok"}

@router.get("")
def list_agents(tenant_id: str):
    """모든 에이전트 목록 조회"""
    return agent_service.list_agents(tenant_id)

@router.get("/{agent_id}")
def get_agent(agent_id: str, tenant_id: str):
    """특정 에이전트 정보 조회"""
    agent = agent_service.get_agent(tenant_id, agent_id)
    if not agent:
        raise HTTPException(404, "에이전트를 찾을 수 없습니다")
    return agent

@router.put("/{agent_id}")
def update_agent(agent_id: str, req: AgentUpdateReq):
    """에이전트 정보 업데이트"""
    agent_service.update_agent(
        req.tenant_id, agent_id, req.name, req.api_id, req.api_hash, req.phone_number
    )
    return {"status": "ok"}

@router.delete("/{agent_id}")
def delete_agent(agent_id: str, tenant_id: str):
    """에이전트 삭제"""
    agent_service.delete_agent(tenant_id, agent_id)
    return {"status": "ok"} 