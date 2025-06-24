import asyncio, json, os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from app.services import mapping_store, openai_service, account_service

# 환경변수에서 OpenAI API 키만 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 에이전트 세션 정보 로드
AGENTS_FILE = "data/agent_sessions.json"
AGENTS = json.load(open(AGENTS_FILE, "r")) if os.path.exists(AGENTS_FILE) else {}

ctx_cache: dict[str, list[dict]] = {}  # (agent:chat) -> messages

async def make_client(agent_id, sess):
    # 에이전트 ID에서 계정 정보 찾기
    account = None
    for account_id, account_info in account_service.list_accounts()["accounts"].items():
        if account_info["phone_number"] == agent_id:
            account = account_info
            break
    
    if not account:
        print(f"Warning: No account found for agent {agent_id}")
        return None
    
    client = TelegramClient(StringSession(sess), account["api_id"], account["api_hash"])

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        mp = mapping_store.get_mapping(agent_id, event.chat_id)
        if not mp: return
        key = f"{agent_id}:{event.chat_id}"
        ctx = ctx_cache.setdefault(key, [])[-10:]

        persona = mapping_store.list_personas()[mp["persona_id"]]
        reply = await openai_service.generate_reply(
            persona["system_prompt"], mp["role"], ctx, event.text
        )
        await asyncio.sleep(mp["delay"])
        await event.respond(reply)
        ctx.extend([
            {"role": "user", "content": event.text},
            {"role": "assistant", "content": reply},
        ])

    await client.start()
    return client

async def main():
    clients = []
    for aid, sess in AGENTS.items():
        client = await make_client(aid, sess)
        if client:
            clients.append(client)
    
    if clients:
        print(f"Running {len(clients)} agents...")
        await asyncio.gather(*[c.run_until_disconnected() for c in clients])
    else:
        print("No valid agents found. Please check your agent_sessions.json and accounts.json")

if __name__ == "__main__":
    asyncio.run(main()) 