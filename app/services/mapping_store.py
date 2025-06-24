import json, os, uuid
from pathlib import Path

DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True)
MAP_FILE  = DATA_PATH / "memberships.json"
PERS_FILE = DATA_PATH / "personas.json"

def _load(path):
    if path.exists():
        return json.loads(path.read_text())
    return {}

def _save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2))

# personas: id -> {name, system_prompt}
def add_persona(name: str, system_prompt: str) -> str:
    pers = _load(PERS_FILE)
    pid = str(uuid.uuid4())
    pers[pid] = {"name": name, "system_prompt": system_prompt}
    _save(PERS_FILE, pers)
    return pid

def list_personas():
    return _load(PERS_FILE)

# memberships: (agent, chat_id) -> {role, persona_id, delay}
def save_mapping(agent_id: str, chat_id: int, role: str, persona_id: str, delay: int):
    mp = _load(MAP_FILE)
    mp_key = f"{agent_id}:{chat_id}"
    mp[mp_key] = {"role": role, "persona_id": persona_id, "delay": delay}
    _save(MAP_FILE, mp)

def get_mapping(agent_id: str, chat_id: int):
    mp = _load(MAP_FILE)
    return mp.get(f"{agent_id}:{chat_id}")

def delete_mapping(agent_id: str, chat_id: int):
    """특정 매핑 삭제"""
    mp = _load(MAP_FILE)
    mp_key = f"{agent_id}:{chat_id}"
    if mp_key in mp:
        del mp[mp_key]
        _save(MAP_FILE, mp)
        return True
    return False

def delete_agent_mappings(agent_id: str):
    """특정 계정의 모든 매핑 삭제"""
    mp = _load(MAP_FILE)
    keys_to_delete = []
    
    for key in mp.keys():
        if key.startswith(f"{agent_id}:"):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del mp[key]
    
    _save(MAP_FILE, mp)
    return len(keys_to_delete) 