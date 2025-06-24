import asyncio, json, os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from app.services import mapping_store, openai_service

API_ID   = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
AGENTS   = json.load(open("data/agent_sessions.json", "r"))  # {agent_id: session_str}

ctx_cache: dict[str, list[dict]] = {}  # (agent:chat) -> messages

async def make_client(agent_id, sess):
    client = TelegramClient(StringSession(sess), API_ID, API_HASH)

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
    clients = [await make_client(aid, sess) for aid, sess in AGENTS.items()]
    print("All agents running.")
    await asyncio.gather(*[c.run_until_disconnected() for c in clients])

if __name__ == "__main__":
    asyncio.run(main()) 