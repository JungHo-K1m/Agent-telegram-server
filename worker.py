import asyncio, os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from app.services import supabase_service, openai_service

# 환경변수에서 OpenAI API 키만 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ctx_cache: dict[str, list[dict]] = {}  # (agent:chat) -> messages

async def make_client(agent_id, sess):
    # 에이전트 ID에서 정보 찾기
    agent = None
    agents = supabase_service.list_agents('test-tenant-id')["agents"]
    for agent_id_key, agent_info in agents.items():
        if agent_info["phone_number"] == agent_id:
            agent = agent_info
            break
    
    if not agent:
        print(f"Warning: No agent found for agent {agent_id}")
        return None
    
    client = TelegramClient(StringSession(sess), agent["api_id"], agent["api_hash"])

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        mp = supabase_service.get_mapping('test-tenant-id', agent_id, event.chat_id)
        if not mp: return
        key = f"{agent_id}:{event.chat_id}"
        ctx = ctx_cache.setdefault(key, [])[-10:]

        persona = supabase_service.get_persona('test-tenant-id', mp["persona_id"])
        if not persona:
            print(f"Warning: No persona found for {mp['persona_id']}")
            return
            
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
    # Supabase에서 활성 세션 로드
    AGENTS = supabase_service.get_active_sessions()
    
    clients = []
    for aid, sess in AGENTS.items():
        client = await make_client(aid, sess)
        if client:
            clients.append(client)
    
    if clients:
        print(f"Running {len(clients)} agents...")
        await asyncio.gather(*[c.run_until_disconnected() for c in clients])
    else:
        print("No valid agents found. Please check your Supabase database")

if __name__ == "__main__":
    asyncio.run(main()) 