from telethon import TelegramClient
from telethon.sessions import StringSession

async def send_code(api_id: int, api_hash: str, phone: str) -> TelegramClient:
    """
    전화번호로 인증 코드를 발송하고, 연결이 유지된 TelegramClient 를 리턴
    """
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()
    try:
        await client.send_code_request(phone)
    except Exception:
        await client.disconnect()
        raise
    return client

async def sign_in(client: TelegramClient, phone: str, code: str, password: str | None):
    """
    수신한 코드(및 2FA 비밀번호)로 로그인 → 세션 스트링 반환
    """
    await client.sign_in(phone=phone, code=code, password=password)
    session_str = client.session.save()
    await client.disconnect()
    return session_str
