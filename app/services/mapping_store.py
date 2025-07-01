from app.services import supabase_service

# personas: id -> {name, system_prompt}
def add_persona(tenant_id: str, name: str, system_prompt: str) -> str:
    return supabase_service.add_persona(tenant_id, name, system_prompt)

def list_personas(tenant_id: str):
    return supabase_service.list_personas(tenant_id)

# memberships: (agent, chat_id) -> {role, persona_id, delay}
def save_mapping(tenant_id: str, agent_id: str, chat_id: int, role: str, persona_id: str, delay: int):
    return supabase_service.save_mapping(tenant_id, agent_id, chat_id, role, persona_id, delay)

def get_mapping(tenant_id: str, agent_id: str, chat_id: int):
    return supabase_service.get_mapping(tenant_id, agent_id, chat_id)

def delete_mapping(tenant_id: str, agent_id: str, chat_id: int):
    return supabase_service.delete_mapping(tenant_id, agent_id, chat_id)

def delete_agent_mappings(tenant_id: str, agent_id: str):
    return supabase_service.delete_agent_mappings(tenant_id, agent_id)

# Supabase 서비스의 함수들을 직접 노출
def _load(path):
    """Supabase에서는 사용하지 않지만 호환성을 위해 유지"""
    return {}

def _save(path, obj):
    """Supabase에서는 사용하지 않지만 호환성을 위해 유지"""
    pass 