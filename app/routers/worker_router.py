from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio

from app.services.worker_service import worker
from utils.logging import log

router = APIRouter(prefix="/worker", tags=["worker"])

class WorkerStatusResponse(BaseModel):
    is_running: bool
    active_agents: int
    total_contexts: int

class AgentControlRequest(BaseModel):
    tenant_id: str
    agent_id: str

@router.get("/status")
async def get_worker_status():
    """워커 상태 조회"""
    return WorkerStatusResponse(
        is_running=worker.is_running,
        active_agents=len(worker.clients),
        total_contexts=len(worker.context_cache)
    )

@router.post("/start")
async def start_worker(background_tasks: BackgroundTasks):
    """워커 시작"""
    if worker.is_running:
        raise HTTPException(400, "Worker is already running")
    
    # 백그라운드에서 워커 시작
    background_tasks.add_task(worker.start_worker)
    
    log.info("Worker start requested")
    return {"status": "starting", "message": "Worker is starting in background"}

@router.post("/stop")
async def stop_worker():
    """워커 중지"""
    if not worker.is_running:
        raise HTTPException(400, "Worker is not running")
    
    await worker.stop_worker()
    
    log.info("Worker stopped")
    return {"status": "stopped", "message": "Worker has been stopped"}

@router.post("/restart")
async def restart_worker(background_tasks: BackgroundTasks):
    """워커 재시작"""
    # 먼저 중지
    if worker.is_running:
        await worker.stop_worker()
    
    # 잠시 대기 후 재시작
    await asyncio.sleep(2)
    
    # 백그라운드에서 워커 시작
    background_tasks.add_task(worker.start_worker)
    
    log.info("Worker restart requested")
    return {"status": "restarting", "message": "Worker is restarting in background"}

@router.post("/add-agent")
async def add_agent_to_worker(req: AgentControlRequest):
    """워커에 에이전트 추가"""
    if not worker.is_running:
        raise HTTPException(400, "Worker is not running")
    
    success = await worker.add_agent(req.tenant_id, req.agent_id)
    if not success:
        raise HTTPException(400, "Failed to add agent to worker")
    
    log.info("Agent added to worker", tenant_id=req.tenant_id, agent_id=req.agent_id)
    return {"status": "success", "message": "Agent added to worker"}

@router.post("/remove-agent")
async def remove_agent_from_worker(req: AgentControlRequest):
    """워커에서 에이전트 제거"""
    if not worker.is_running:
        raise HTTPException(400, "Worker is not running")
    
    success = await worker.remove_agent(req.tenant_id, req.agent_id)
    if not success:
        raise HTTPException(400, "Failed to remove agent from worker")
    
    log.info("Agent removed from worker", tenant_id=req.tenant_id, agent_id=req.agent_id)
    return {"status": "success", "message": "Agent removed from worker"}

@router.get("/agents")
async def list_active_agents():
    """활성 에이전트 목록 조회"""
    agents = []
    for client_key, client in worker.clients.items():
        tenant_id, agent_id = client_key.split(":", 1)
        agents.append({
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "is_connected": client.is_connected()
        })
    
    return {
        "active_agents": agents,
        "total_count": len(agents)
    }

@router.get("/contexts")
async def list_contexts():
    """컨텍스트 캐시 목록 조회"""
    contexts = []
    for context_key, messages in worker.context_cache.items():
        tenant_id, agent_id, chat_id = context_key.split(":", 2)
        contexts.append({
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "chat_id": chat_id,
            "message_count": len(messages)
        })
    
    return {
        "contexts": contexts,
        "total_count": len(contexts)
    } 