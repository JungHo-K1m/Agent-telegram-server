from supabase import create_client, Client
from typing import Dict, List, Optional, Any
from app.config import settings
import uuid

# Supabase 클라이언트 초기화 (지연 초기화)
supabase: Optional[Client] = None

def _get_supabase_client() -> Client:
    """Supabase 클라이언트를 지연 초기화"""
    global supabase
    if supabase is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise Exception("Supabase 환경변수가 설정되지 않았습니다. SUPABASE_URL과 SUPABASE_ANON_KEY를 설정해주세요.")
        supabase = create_client(settings.supabase_url, settings.supabase_key)
    return supabase

# ===== ACCOUNTS =====
def add_agent(tenant_id: str, name: str, api_id: int, api_hash: str, phone_number: str) -> str:
    """새 에이전트 추가"""
    client = _get_supabase_client()
    data = {
        "tenant_id": tenant_id,
        "name": name,
        "api_id": api_id,
        "api_hash": api_hash,
        "phone_number": phone_number
    }
    result = client.table("agents").insert(data).execute()
    return result.data[0]["id"]

def get_agent(tenant_id: str, agent_id: str) -> Optional[Dict]:
    """특정 에이전트 정보 조회 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("agents").select("*").eq("tenant_id", tenant_id).eq("id", agent_id).execute()
    if result.data:
        return result.data[0]
    return None

def list_agents(tenant_id: str) -> Dict:
    """모든 에이전트 목록 조회 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("agents").select("*").eq("tenant_id", tenant_id).execute()
    agents = {}
    for agent in result.data:
        agents[agent["id"]] = {
            "name": agent["name"],
            "api_id": agent["api_id"],
            "api_hash": agent["api_hash"],
            "phone_number": agent["phone_number"],
            "session_string": agent.get("session_string"),
            "created_at": agent.get("created_at")
        }
    return {"agents": agents}

def update_agent(tenant_id: str, agent_id: str, **kwargs) -> bool:
    """에이전트 정보 업데이트 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("agents").update(kwargs).eq("tenant_id", tenant_id).eq("id", agent_id).execute()
    return len(result.data) > 0

def delete_agent(tenant_id: str, agent_id: str) -> bool:
    """에이전트 삭제 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("agents").delete().eq("tenant_id", tenant_id).eq("id", agent_id).execute()
    return len(result.data) > 0

# ===== PERSONAS =====
def add_persona(tenant_id: str, name: str, system_prompt: str) -> str:
    """새 페르소나 추가"""
    client = _get_supabase_client()
    data = {
        "tenant_id": tenant_id,
        "name": name,
        "system_prompt": system_prompt
    }
    result = client.table("personas").insert(data).execute()
    return result.data[0]["id"]

def list_personas(tenant_id: str) -> Dict:
    """모든 페르소나 목록 조회 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("personas").select("*").eq("tenant_id", tenant_id).execute()
    personas = {}
    for persona in result.data:
        personas[persona["id"]] = {
            "name": persona["name"],
            "system_prompt": persona["system_prompt"]
        }
    return personas

def get_persona(tenant_id: str, persona_id: str) -> Optional[Dict]:
    """특정 페르소나 조회 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("personas").select("*").eq("tenant_id", tenant_id).eq("id", persona_id).execute()
    if result.data:
        return result.data[0]
    return None

def update_persona(tenant_id: str, persona_id: str, **kwargs) -> bool:
    """페르소나 업데이트 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("personas").update(kwargs).eq("tenant_id", tenant_id).eq("id", persona_id).execute()
    return len(result.data) > 0

def delete_persona(tenant_id: str, persona_id: str) -> bool:
    """페르소나 삭제 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("personas").delete().eq("tenant_id", tenant_id).eq("id", persona_id).execute()
    return len(result.data) > 0

# ===== MAPPINGS =====
def save_mapping(tenant_id: str, agent_id: str, chat_id: int, role: str, persona_id: str, delay: int) -> str:
    """매핑 저장 (upsert)"""
    client = _get_supabase_client()
    data = {
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "chat_id": chat_id,
        "role": role,
        "persona_id": persona_id,
        "delay_sec": delay
    }
    result = client.table("mappings").upsert(data, on_conflict="tenant_id,agent_id,chat_id").execute()
    return result.data[0]["id"]

def get_mapping(tenant_id: str, agent_id: str, chat_id: int) -> Optional[Dict]:
    """특정 매핑 조회 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("mappings").select("*").eq("tenant_id", tenant_id).eq("agent_id", agent_id).eq("chat_id", chat_id).execute()
    if result.data:
        mapping = result.data[0]
        return {
            "role": mapping["role"],
            "persona_id": mapping["persona_id"],
            "delay": mapping["delay_sec"]
        }
    return None

def list_all_mappings(tenant_id: str) -> Dict:
    """모든 매핑 조회 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("mappings").select("*").eq("tenant_id", tenant_id).execute()
    mappings = {}
    for mapping in result.data:
        key = f"{mapping['agent_id']}:{mapping['chat_id']}"
        mappings[key] = {
            "role": mapping["role"],
            "persona_id": mapping["persona_id"],
            "delay": mapping["delay_sec"]
        }
    return mappings

def list_agent_mappings(tenant_id: str, agent_id: str) -> Dict:
    """특정 에이전트의 모든 매핑 조회 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("mappings").select("*").eq("tenant_id", tenant_id).eq("agent_id", agent_id).execute()
    mappings = {}
    for mapping in result.data:
        mappings[str(mapping["chat_id"])] = {
            "role": mapping["role"],
            "persona_id": mapping["persona_id"],
            "delay": mapping["delay_sec"]
        }
    return mappings

def update_mapping(tenant_id: str, agent_id: str, chat_id: int, **kwargs) -> bool:
    """매핑 업데이트 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("mappings").update(kwargs).eq("tenant_id", tenant_id).eq("agent_id", agent_id).eq("chat_id", chat_id).execute()
    return len(result.data) > 0

def delete_mapping(tenant_id: str, agent_id: str, chat_id: int) -> bool:
    """특정 매핑 삭제 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("mappings").delete().eq("tenant_id", tenant_id).eq("agent_id", agent_id).eq("chat_id", chat_id).execute()
    return len(result.data) > 0

def delete_agent_mappings(tenant_id: str, agent_id: str) -> int:
    """에이전트의 모든 매핑 삭제 (테넌트별)"""
    client = _get_supabase_client()
    result = client.table("mappings").delete().eq("tenant_id", tenant_id).eq("agent_id", agent_id).execute()
    return len(result.data)

# ===== AGENT SESSIONS =====
def save_agent_session(agent_id: str, session_string: str) -> str:
    """에이전트 세션 저장"""
    client = _get_supabase_client()
    
    # agent_id가 agents 테이블에 존재하는지 확인
    account_result = client.table("agents").select("phone_number").eq("phone_number", agent_id).execute()
    if not account_result.data:
        raise Exception(f"Agent ID {agent_id}에 해당하는 에이전트가 agents 테이블에 존재하지 않습니다.")
    
    # 기존 세션 비활성화
    client.table("agent_sessions").update({"is_active": False}).eq("agent_id", agent_id).execute()
    
    # 새 세션 저장
    data = {
        "agent_id": agent_id,
        "session_string": session_string,
        "is_active": True
    }
    result = client.table("agent_sessions").insert(data).execute()
    return result.data[0]["id"]

def get_agent_session(agent_id: str) -> Optional[str]:
    """특정 에이전트의 활성 세션 스트링 조회"""
    client = _get_supabase_client()
    result = client.table("agent_sessions").select("session_string").eq("agent_id", agent_id).eq("is_active", True).execute()
    if result.data:
        return result.data[0]["session_string"]
    return None

def get_agent_session_with_tenant(tenant_id: str, agent_id: str) -> Optional[Dict]:
    """테넌트별 특정 에이전트의 세션 정보 조회"""
    client = _get_supabase_client()
    
    # 먼저 에이전트가 해당 테넌트에 속하는지 확인
    agent_result = client.table("agents").select("id, phone_number").eq("tenant_id", tenant_id).eq("id", agent_id).execute()
    if not agent_result.data:
        return None
    
    phone_number = agent_result.data[0]["phone_number"]
    
    # 해당 에이전트의 활성 세션 조회
    session_result = client.table("agent_sessions").select("*").eq("agent_id", phone_number).eq("is_active", True).execute()
    if session_result.data:
        session = session_result.data[0]
        return {
            "agent_id": agent_id,
            "phone_number": phone_number,
            "session_string": session["session_string"],
            "is_active": session["is_active"],
            "created_at": session.get("created_at")
        }
    return None

def list_tenant_sessions(tenant_id: str) -> Dict:
    """테넌트의 모든 에이전트 세션 조회"""
    client = _get_supabase_client()
    
    # 테넌트의 모든 에이전트 조회
    agents_result = client.table("agents").select("id, phone_number, name").eq("tenant_id", tenant_id).execute()
    
    sessions = {}
    for agent in agents_result.data:
        phone_number = agent["phone_number"]
        
        # 각 에이전트의 활성 세션 조회
        session_result = client.table("agent_sessions").select("*").eq("agent_id", phone_number).eq("is_active", True).execute()
        
        if session_result.data:
            session = session_result.data[0]
            sessions[agent["id"]] = {
                "agent_id": agent["id"],
                "name": agent["name"],
                "phone_number": phone_number,
                "session_string": session["session_string"],
                "is_active": session["is_active"],
                "created_at": session.get("created_at")
            }
        else:
            # 세션이 없는 경우
            sessions[agent["id"]] = {
                "agent_id": agent["id"],
                "name": agent["name"],
                "phone_number": phone_number,
                "session_string": None,
                "is_active": False,
                "created_at": None
            }
    
    return sessions

def get_active_sessions() -> Dict:
    """활성 세션 목록 조회"""
    client = _get_supabase_client()
    result = client.table("agent_sessions").select("*").eq("is_active", True).execute()
    sessions = {}
    for session in result.data:
        sessions[session["agent_id"]] = session["session_string"]
    return sessions

def deactivate_session(agent_id: str) -> bool:
    """세션 비활성화"""
    client = _get_supabase_client()
    result = client.table("agent_sessions").update({"is_active": False}).eq("agent_id", agent_id).execute()
    return len(result.data) > 0 