from app.services import supabase_service

def add_account(account_id: str, name: str, api_id: int, api_hash: str, phone_number: str):
    return supabase_service.add_account(account_id, name, api_id, api_hash, phone_number)

def get_account(account_id: str):
    return supabase_service.get_account(account_id)

def list_accounts():
    return supabase_service.list_accounts()

def update_account(account_id: str, **kwargs):
    return supabase_service.update_account(account_id, **kwargs)

def delete_account(account_id: str):
    return supabase_service.delete_account(account_id) 