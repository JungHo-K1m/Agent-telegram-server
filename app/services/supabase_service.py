from supabase import create_client, Client
from typing import Dict, List, Optional, Any
from app.config import settings
import uuid

# Supabase 클라이언트 초기화
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

# ===== ACCOUNTS =====
def add_account(account_id: str, name: str, api_id: int, api_hash: str, phone_number: str) -> str:
    """새 계정 추가"""
    data = {
        "id": account_id,
        "name": name,
        "api_id": api_id,
        "api_hash": api_hash,
        "phone_number": phone_number
    }
    result = supabase.table("accounts").insert(data).execute()
    return account_id

def get_account(account_id: str) -> Optional[Dict]:
    """계정 정보 조회"""
    result = supabase.table("accounts").select("*").eq("id", account_id).execute()
    if result.data:
        return result.data[0]
    return None

def list_accounts() -> Dict:
    """모든 계정 목록 조회"""
    result = supabase.table("accounts").select("*").execute()
    accounts = {}
    for account in result.data:
        accounts[account["id"]] = {
            "name": account["name"],
            "api_id": account["api_id"],
            "api_hash": account["api_hash"],
            "phone_number": account["phone_number"]
        }
    return {"accounts": accounts}

def update_account(account_id: str, **kwargs) -> bool:
    """계정 정보 업데이트"""
    result = supabase.table("accounts").update(kwargs).eq("id", account_id).execute()
    return len(result.data) > 0

def delete_account(account_id: str) -> bool:
    """계정 삭제"""
    result = supabase.table("accounts").delete().eq("id", account_id).execute()
    return len(result.data) > 0

# ===== PERSONAS =====
def add_persona(name: str, system_prompt: str) -> str:
    """새 페르소나 추가"""
    data = {
        "name": name,
        "system_prompt": system_prompt
    }
    result = supabase.table("personas").insert(data).execute()
    return result.data[0]["id"]

def list_personas() -> Dict:
    """모든 페르소나 목록 조회"""
    result = supabase.table("personas").select("*").execute()
    personas = {}
    for persona in result.data:
        personas[persona["id"]] = {
            "name": persona["name"],
            "system_prompt": persona["system_prompt"]
        }
    return personas

def get_persona(persona_id: str) -> Optional[Dict]:
    """특정 페르소나 조회"""
    result = supabase.table("personas").select("*").eq("id", persona_id).execute()
    if result.data:
        return result.data[0]
    return None

def update_persona(persona_id: str, **kwargs) -> bool:
    """페르소나 업데이트"""
    result = supabase.table("personas").update(kwargs).eq("id", persona_id).execute()
    return len(result.data) > 0

def delete_persona(persona_id: str) -> bool:
    """페르소나 삭제"""
    result = supabase.table("personas").delete().eq("id", persona_id).execute()
    return len(result.data) > 0

# ===== MAPPINGS =====
def save_mapping(agent_id: str, chat_id: int, role: str, persona_id: str, delay: int) -> str:
    """매핑 저장 (upsert)"""
    data = {
        "agent_id": agent_id,
        "chat_id": chat_id,
        "role": role,
        "persona_id": persona_id,
        "delay_sec": delay
    }
    result = supabase.table("mappings").upsert(data, on_conflict="agent_id,chat_id").execute()
    return result.data[0]["id"]

def get_mapping(agent_id: str, chat_id: int) -> Optional[Dict]:
    """특정 매핑 조회"""
    result = supabase.table("mappings").select("*").eq("agent_id", agent_id).eq("chat_id", chat_id).execute()
    if result.data:
        mapping = result.data[0]
        return {
            "role": mapping["role"],
            "persona_id": mapping["persona_id"],
            "delay": mapping["delay_sec"]
        }
    return None

def list_all_mappings() -> Dict:
    """모든 매핑 조회"""
    result = supabase.table("mappings").select("*").execute()
    mappings = {}
    for mapping in result.data:
        key = f"{mapping['agent_id']}:{mapping['chat_id']}"
        mappings[key] = {
            "role": mapping["role"],
            "persona_id": mapping["persona_id"],
            "delay": mapping["delay_sec"]
        }
    return mappings

def list_agent_mappings(agent_id: str) -> Dict:
    """특정 계정의 모든 매핑 조회"""
    result = supabase.table("mappings").select("*").eq("agent_id", agent_id).execute()
    mappings = {}
    for mapping in result.data:
        mappings[str(mapping["chat_id"])] = {
            "role": mapping["role"],
            "persona_id": mapping["persona_id"],
            "delay": mapping["delay_sec"]
        }
    return mappings

def update_mapping(agent_id: str, chat_id: int, **kwargs) -> bool:
    """매핑 업데이트"""
    result = supabase.table("mappings").update(kwargs).eq("agent_id", agent_id).eq("chat_id", chat_id).execute()
    return len(result.data) > 0

def delete_mapping(agent_id: str, chat_id: int) -> bool:
    """특정 매핑 삭제"""
    result = supabase.table("mappings").delete().eq("agent_id", agent_id).eq("chat_id", chat_id).execute()
    return len(result.data) > 0

def delete_agent_mappings(agent_id: str) -> int:
    """계정의 모든 매핑 삭제"""
    result = supabase.table("mappings").delete().eq("agent_id", agent_id).execute()
    return len(result.data)

# ===== AGENT SESSIONS =====
def save_agent_session(agent_id: str, session_string: str) -> str:
    """에이전트 세션 저장"""
    # 기존 세션 비활성화
    supabase.table("agent_sessions").update({"is_active": False}).eq("agent_id", agent_id).execute()
    
    # 새 세션 저장
    data = {
        "agent_id": agent_id,
        "session_string": session_string,
        "is_active": True
    }
    result = supabase.table("agent_sessions").insert(data).execute()
    return result.data[0]["id"]

def get_active_sessions() -> Dict:
    """활성 세션 목록 조회"""
    result = supabase.table("agent_sessions").select("*").eq("is_active", True).execute()
    sessions = {}
    for session in result.data:
        sessions[session["agent_id"]] = session["session_string"]
    return sessions

def deactivate_session(agent_id: str) -> bool:
    """세션 비활성화"""
    result = supabase.table("agent_sessions").update({"is_active": False}).eq("agent_id", agent_id).execute()
    return len(result.data) > 0 