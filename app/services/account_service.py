import json
from pathlib import Path
from typing import Dict, List, Optional

DATA_PATH = Path("data")
ACCOUNTS_FILE = DATA_PATH / "accounts.json"

def _load_accounts() -> Dict:
    """계정 정보 로드"""
    if ACCOUNTS_FILE.exists():
        return json.loads(ACCOUNTS_FILE.read_text())
    return {"accounts": {}}

def _save_accounts(accounts: Dict):
    """계정 정보 저장"""
    ACCOUNTS_FILE.write_text(json.dumps(accounts, ensure_ascii=False, indent=2))

def add_account(account_id: str, name: str, api_id: int, api_hash: str, phone_number: str):
    """새 계정 추가"""
    accounts = _load_accounts()
    accounts["accounts"][account_id] = {
        "name": name,
        "api_id": api_id,
        "api_hash": api_hash,
        "phone_number": phone_number
    }
    _save_accounts(accounts)

def get_account(account_id: str) -> Optional[Dict]:
    """계정 정보 조회"""
    accounts = _load_accounts()
    return accounts["accounts"].get(account_id)

def list_accounts() -> Dict:
    """모든 계정 목록 조회"""
    return _load_accounts()

def delete_account(account_id: str):
    """계정 삭제"""
    accounts = _load_accounts()
    if account_id in accounts["accounts"]:
        del accounts["accounts"][account_id]
        _save_accounts(accounts)

def update_account(account_id: str, name: str = None, api_id: int = None, 
                  api_hash: str = None, phone_number: str = None):
    """계정 정보 업데이트"""
    accounts = _load_accounts()
    if account_id in accounts["accounts"]:
        account = accounts["accounts"][account_id]
        if name: account["name"] = name
        if api_id: account["api_id"] = api_id
        if api_hash: account["api_hash"] = api_hash
        if phone_number: account["phone_number"] = phone_number
        _save_accounts(accounts) 