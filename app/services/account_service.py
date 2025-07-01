from app.services import supabase_service

def add_account(tenant_id: str, account_id: str, name: str, api_id: int, api_hash: str, phone_number: str):
    return supabase_service.add_account(tenant_id, account_id, name, api_id, api_hash, phone_number)

def get_account(tenant_id: str, account_id: str):
    return supabase_service.get_account(tenant_id, account_id)

def list_accounts(tenant_id: str):
    return supabase_service.list_accounts(tenant_id)

def update_account(tenant_id: str, account_id: str, name=None, api_id=None, api_hash=None, phone_number=None):
    return supabase_service.update_account(tenant_id, account_id, name=name, api_id=api_id, api_hash=api_hash, phone_number=phone_number)

def delete_account(tenant_id: str, account_id: str):
    return supabase_service.delete_account(tenant_id, account_id) 