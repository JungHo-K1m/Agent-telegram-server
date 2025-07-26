import os, asyncio
import openai
import re
import time
from typing import List, Dict

# OpenAI 클라이언트 초기화 (1.0+ 버전)
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ROLE_GUIDE = {
    "Chatter":   "You are a friendly content sharer. Respond naturally like a real person.",
    "Moderator": "You are a strict but polite moderator.",
    "Admin":     "You are the system administrator bot.",
}

# 연속 메시지 추적을 위한 전역 변수
message_buffer = {}  # {chat_id: {"messages": [], "last_time": timestamp}}

def is_incomplete_sentence(text: str) -> bool:
    """문장이 완성되지 않았는지 판단"""
    
    # 1. 문장 끝 표시가 없는 경우
    sentence_endings = ['.', '!', '?', '~', '...']
    has_ending = any(text.endswith(ending) for ending in sentence_endings)
    
    # 2. 짧은 단어들로 끝나는 경우 (추가 입력 예상)
    incomplete_endings = [
        '이', '가', '을', '를', '의', '에', '로', '와', '과',
        '은', '는', '도', '만', '부터', '까지', '에서', '에게',
        '안녕', '오늘', '내일', '어제', '지금', '나중에',
        '그리고', '하지만', '그런데', '그래서', '그러면'
    ]
    
    ends_with_incomplete = any(text.endswith(word) for word in incomplete_endings)
    
    # 3. 숫자나 특수문자로 끝나는 경우
    ends_with_number = text[-1].isdigit() if text else False
    ends_with_symbol = text[-1] in '+-*/=()[]{}' if text else False
    
    # 4. 한 글자로 끝나는 경우
    is_single_char = len(text.strip()) == 1
    
    return not has_ending or ends_with_incomplete or ends_with_number or ends_with_symbol or is_single_char

def should_wait_for_more_messages(chat_id: str, current_message: str, context: list[dict] = None) -> bool:
    """더 많은 메시지를 기다려야 하는지 판단"""
    
    global message_buffer
    
    # 1. 현재 시간
    current_time = time.time()
    
    # 2. 채팅방별 메시지 버퍼 초기화
    if chat_id not in message_buffer:
        message_buffer[chat_id] = {
            "messages": [],
            "last_time": current_time
        }
    
    buffer = message_buffer[chat_id]
    
    # 3. 시간이 너무 오래 지났으면 버퍼 초기화 (30초)
    if current_time - buffer["last_time"] > 30:
        buffer["messages"] = []
    
    # 4. 현재 메시지를 버퍼에 추가
    buffer["messages"].append(current_message)
    buffer["last_time"] = current_time
    
    # 5. 연속 메시지인지 판단
    if len(buffer["messages"]) == 1:
        # 첫 번째 메시지인 경우
        return is_incomplete_sentence(current_message)
    
    # 6. 여러 메시지가 있는 경우
    combined_message = " ".join(buffer["messages"])
    
    # 7. 완성된 문장인지 확인
    if not is_incomplete_sentence(combined_message):
        # 완성된 문장이면 버퍼 초기화
        buffer["messages"] = []
        return False
    
    # 8. 아직 완성되지 않았으면 더 기다림
    return True

def get_combined_message(chat_id: str) -> str:
    """버퍼의 모든 메시지를 합쳐서 반환"""
    global message_buffer
    
    if chat_id in message_buffer:
        combined = " ".join(message_buffer[chat_id]["messages"])
        message_buffer[chat_id]["messages"] = []  # 버퍼 초기화
        return combined
    
    return ""

async def should_respond_to_message(message: str, context: list[dict] = None, chat_id: str = None) -> bool:
    """메시지에 답변해야 할지 판단"""
    
    # 1. 연속 메시지 처리
    if chat_id and should_wait_for_more_messages(chat_id, message, context):
        return False  # 더 기다림
    
    # 실제 처리할 메시지 (연속 메시지가 합쳐진 것)
    actual_message = get_combined_message(chat_id) if chat_id else message
    
    # 2. 명백한 무의미한 메시지 필터링
    meaningless_patterns = [
        r'^[ㅋㅎ]+$',  # 웃음만
        r'^[ㅇㅎ]+$',  # 추임새만
        r'^[.]{2,}$',  # 점만
        r'^[~]{2,}$',  # 물결만
        r'^[!]{2,}$',  # 느낌표만
        r'^[?]{2,}$',  # 물음표만
        r'^[ㅁㅇㅎ]+$',  # 추임새 조합
        r'^[ㅋㅎ!~.]+$',  # 감정 표현만
    ]
    
    for pattern in meaningless_patterns:
        if re.match(pattern, actual_message.strip()):
            return False
    
    # 3. 짧은 추임새 필터링
    short_responses = ['음', '어', '응', '그래', '맞아', '좋아', 'ㅇㅇ', 'ㅇ', 'ㅎ', 'ㅋ']
    if actual_message.strip() in short_responses:
        return False
    
    # 4. AI에게 질문하는지 판단
    question_keywords = ['?', '뭐', '무엇', '어떻게', '왜', '언제', '어디', '누가', '몇']
    has_question = any(keyword in actual_message for keyword in question_keywords)
    
    # 5. 맥락 기반 판단 (AI에게 직접 언급)
    direct_mentions = ['너', '당신', 'AI', '봇', '기계', '로봇']
    is_direct_mention = any(mention in actual_message for mention in direct_mentions)
    
    # 6. 대화 맥락 분석 (선택사항)
    if context and len(context) > 0:
        # 최근 대화에서 AI가 언급되었는지 확인
        recent_context = context[-3:]  # 최근 3개 메시지
        for msg in recent_context:
            if msg.get('role') == 'assistant':
                # AI가 최근에 언급되었다면 더 적극적으로 응답
                return True
    
    # 7. 최종 판단
    # 질문이 있거나 직접 언급이 있으면 응답
    if has_question or is_direct_mention:
        return True
    
    # 긴 메시지(10자 이상)는 응답
    if len(actual_message.strip()) >= 10:
        return True
    
    # 짧은 메시지는 30% 확률로만 응답 (자연스러움)
    import random
    return random.random() < 0.3

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