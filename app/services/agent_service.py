from app.services import supabase_service

def add_agent(tenant_id: str, name: str, api_id: int, api_hash: str, phone_number: str):
    return supabase_service.add_agent(tenant_id, name, api_id, api_hash, phone_number)

def get_agent(tenant_id: str, agent_id: str):
    return supabase_service.get_agent(tenant_id, agent_id)

def list_agents(tenant_id: str):
    return supabase_service.list_agents(tenant_id)

def update_agent(tenant_id: str, agent_id: str, name=None, api_id=None, api_hash=None, phone_number=None):
    return supabase_service.update_agent(tenant_id, agent_id, name=name, api_id=api_id, api_hash=api_hash, phone_number=phone_number)

def delete_agent(tenant_id: str, agent_id: str):
    return supabase_service.delete_agent(tenant_id, agent_id) 