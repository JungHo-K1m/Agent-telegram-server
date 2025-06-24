import os, asyncio
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

ROLE_GUIDE = {
    "Chatter":   "You are a friendly content sharer.",
    "Moderator": "You are a strict but polite moderator.",
    "Admin":     "You are the system administrator bot.",
}

async def generate_reply(persona_prompt: str, role: str, context: list[dict], user_msg: str):
    messages = (
        context
        + [{"role": "system", "content": persona_prompt}]
        + [{"role": "assistant", "content": ROLE_GUIDE[role]}]
        + [{"role": "user", "content": user_msg}]
    )

    resp = await openai.ChatCompletion.acreate(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
    )
    return resp.choices[0].message.content 