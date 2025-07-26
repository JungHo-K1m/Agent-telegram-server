import os, asyncio
import openai
import re
from typing import List, Dict

# OpenAI 클라이언트 초기화 (1.0+ 버전)
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ROLE_GUIDE = {
    "Chatter":   "You are a friendly content sharer. Respond naturally like a real person.",
    "Moderator": "You are a strict but polite moderator.",
    "Admin":     "You are the system administrator bot.",
}

async def generate_reply(persona_prompt: str, role: str, context: list[dict], user_msg: str):
    """기본 응답 생성"""
    messages = (
        context
        + [{"role": "system", "content": persona_prompt}]
        + [{"role": "assistant", "content": ROLE_GUIDE[role]}]
        + [{"role": "user", "content": user_msg}]
    )

    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
    )
    return resp.choices[0].message.content

async def generate_multi_reply(persona_prompt: str, role: str, context: list[dict], user_msg: str, chat_participants: List[str] = None):
    """여러 명에게 답장하는 응답 생성"""
    
    # 시스템 프롬프트에 멀티 리플라이 가이드 추가
    multi_reply_guide = """
    You are in a group chat. When responding to multiple people or complex situations:
    1. You can respond to multiple people in one message
    2. You can split your response into multiple messages if it's more natural
    3. Use @username to mention specific people when needed
    4. Keep responses conversational and natural
    5. If the conversation involves multiple topics, address them separately
    
    Format your response as:
    - Single response: Just write normally
    - Multiple responses: Use "---SPLIT---" to separate different messages
    Example:
    "Hey @john, that's a great point! ---SPLIT--- @sarah, I think you're right about that too."
    """
    
    enhanced_prompt = persona_prompt + "\n\n" + multi_reply_guide
    
    messages = (
        context
        + [{"role": "system", "content": enhanced_prompt}]
        + [{"role": "assistant", "content": ROLE_GUIDE[role]}]
        + [{"role": "user", "content": user_msg}]
    )

    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
    )
    
    response_text = resp.choices[0].message.content
    
    # 응답을 여러 개로 분할
    if "---SPLIT---" in response_text:
        return [msg.strip() for msg in response_text.split("---SPLIT---") if msg.strip()]
    else:
        return [response_text]

async def generate_natural_reply(persona_prompt: str, role: str, context: list[dict], user_msg: str):
    """자연스러운 응답 생성 (타이핑 효과, 지연 등)"""
    
    natural_guide = """
    You are a real person in a group chat. Be natural and conversational:
    1. Use casual language and emojis when appropriate
    2. Show personality and emotion
    3. Sometimes use "..." or "hmm" to show thinking
    4. Be responsive to the conversation flow
    5. Don't be too formal or robotic
    """
    
    enhanced_prompt = persona_prompt + "\n\n" + natural_guide
    
    messages = (
        context
        + [{"role": "system", "content": enhanced_prompt}]
        + [{"role": "assistant", "content": ROLE_GUIDE[role]}]
        + [{"role": "user", "content": user_msg}]
    )

    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.8,  # 더 창의적인 응답
    )
    
    return resp.choices[0].message.content 