import asyncio
import os
from typing import Dict, List, Optional, Any
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import structlog
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

from app.services import supabase_service, openai_service
from utils.logging import log

# 로거 설정
logger = structlog.get_logger()

class TelegramWorker:
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.context_cache: Dict[str, List[Dict]] = {}  # (tenant_id:agent_id:chat_id) -> messages
        self.is_running = False
        
    async def start_worker(self):
        """워커 시작 - 모든 활성 에이전트에 대한 클라이언트 생성"""
        if self.is_running:
            logger.warning("Worker is already running")
            return
            
        self.is_running = True
        logger.info("Starting Telegram Worker")
        
        try:
            # 모든 테넌트의 활성 세션 조회
            active_sessions = await self._get_all_active_sessions()
            
            if not active_sessions:
                logger.warning("No active sessions found")
                return
                
            # 각 에이전트에 대한 클라이언트 생성
            for session_info in active_sessions:
                await self._create_client(session_info)
                
            if self.clients:
                logger.info(f"Started {len(self.clients)} agents", agent_count=len(self.clients))
                # 모든 클라이언트를 병렬로 실행
                await asyncio.gather(*[client.run_until_disconnected() for client in self.clients.values()])
            else:
                logger.warning("No valid clients created")
                
        except Exception as e:
            logger.error("Worker failed", error=str(e))
            raise
        finally:
            self.is_running = False
            
    async def stop_worker(self):
        """워커 중지"""
        logger.info("Stopping Telegram Worker")
        self.is_running = False
        
        # 모든 클라이언트 연결 해제
        for client in self.clients.values():
            if client.is_connected():
                await client.disconnect()
        self.clients.clear()
        self.context_cache.clear()
        
    async def _get_all_active_sessions(self) -> List[Dict]:
        """모든 테넌트의 활성 에이전트 조회 (session_string이 agents 테이블에 직접 저장됨)"""
        client = supabase_service._get_supabase_client()
        
        try:
            # agents 테이블에서 활성 에이전트와 세션 정보 조회
            result = client.table("agents").select(
                "id, tenant_id, name, api_id, api_hash, phone_number, session_string"
            ).eq("is_active", True).not_.is_("session_string", "null").execute()
            
            sessions = []
            for agent in result.data:
                if agent.get("session_string"):  # 세션이 있는 에이전트만
                    sessions.append({
                        "tenant_id": agent["tenant_id"],
                        "agent_id": agent["id"],
                        "phone_number": agent["phone_number"],
                        "name": agent["name"],
                        "api_id": agent["api_id"],
                        "api_hash": agent["api_hash"],
                        "session_string": agent["session_string"]
                    })
            
            logger.info(f"활성 에이전트 {len(sessions)}개 발견")
            return sessions
            
        except Exception as e:
            logger.error(f"활성 에이전트 조회 실패: {e}")
            return []
        
    async def _create_client(self, session_info: Dict):
        """텔레그램 클라이언트 생성 및 이벤트 핸들러 설정"""
        try:
            # Telegram API 정보 직접 설정
            api_id = 25060740
            api_hash = "f93d24a5fba99007d0a81a28ab5ca7bc"
            
            client = TelegramClient(
                StringSession(session_info["session_string"]),
                api_id,
                api_hash
            )
            
            # 메시지 핸들러 등록
            @client.on(events.NewMessage(incoming=True))
            async def message_handler(event):
                await self._handle_message(session_info, event)
                
            # 클라이언트 시작
            await client.start()
            
            # 클라이언트 저장
            client_key = f"{session_info['tenant_id']}:{session_info['agent_id']}"
            self.clients[client_key] = client
            
            logger.info("Client created successfully", 
                       tenant_id=session_info["tenant_id"],
                       agent_id=session_info["agent_id"],
                       agent_name=session_info["name"])
                       
        except Exception as e:
            logger.error("Failed to create client", 
                        tenant_id=session_info["tenant_id"],
                        agent_id=session_info["agent_id"],
                        error=str(e))
            
    async def _handle_message(self, session_info: Dict, event):
        """텔레그램 메시지 처리"""
        try:
            tenant_id = session_info["tenant_id"]
            agent_id = session_info["agent_id"]
            chat_id = event.chat_id
            
            # agent_chat_configs에서 매핑 정보 조회
            mapping = await self._get_chat_config(tenant_id, agent_id, chat_id)
            if not mapping:
                logger.debug("No chat config found for chat", 
                           tenant_id=tenant_id,
                           agent_id=agent_id,
                           chat_id=chat_id)
                return
                
            # 페르소나 정보 조회
            persona = await self._get_persona(tenant_id, mapping["persona_id"])
            if not persona:
                logger.warning("Persona not found", 
                             tenant_id=tenant_id,
                             persona_id=mapping["persona_id"])
                return
                
            # 컨텍스트 캐시 키
            context_key = f"{tenant_id}:{agent_id}:{chat_id}"
            context = self.context_cache.setdefault(context_key, [])
            
            # 최근 10개 메시지만 유지
            if len(context) > 20:
                context = context[-20:]
                self.context_cache[context_key] = context
                
            # OpenAI 응답 생성
            reply = await openai_service.generate_reply(
                persona["system_prompt"],
                mapping["role"],
                context,
                event.text
            )
            
            # 응답 지연
            await asyncio.sleep(mapping["delay"])
            
            # 메시지 전송
            await event.respond(reply)
            
            # 메시지 저장 (messages 테이블에 직접 저장)
            try:
                client = supabase_service._get_supabase_client()
                client.table("messages").insert({
                    "tenant_id": tenant_id,
                    "chat_id": chat_id,
                    "agent_id": agent_id,
                    "content": reply,
                    "user_id": None  # AI 응답이므로 user_id는 None
                }).execute()
            except Exception as e:
                logger.error(f"메시지 저장 실패: {e}")
            
            # 컨텍스트 업데이트
            context.extend([
                {"role": "user", "content": event.text},
                {"role": "assistant", "content": reply}
            ])
            
            logger.info("Message processed successfully",
                       tenant_id=tenant_id,
                       agent_id=agent_id,
                       chat_id=chat_id,
                       message_length=len(event.text),
                       reply_length=len(reply))
                       
        except Exception as e:
            logger.error("Failed to process message",
                        tenant_id=session_info.get("tenant_id"),
                        agent_id=session_info.get("agent_id"),
                        chat_id=getattr(event, 'chat_id', None),
                        error=str(e))
                        
    async def add_agent(self, tenant_id: str, agent_id: str):
        """새로운 에이전트 추가"""
        try:
            # agents 테이블에서 에이전트 정보 조회
            client = supabase_service._get_supabase_client()
            result = client.table("agents").select(
                "id, tenant_id, name, api_id, api_hash, phone_number, session_string, is_active"
            ).eq("id", agent_id).eq("tenant_id", tenant_id).execute()
            
            if not result.data:
                logger.warning("Agent not found",
                             tenant_id=tenant_id,
                             agent_id=agent_id)
                return False
                
            agent_info = result.data[0]
            
            if not agent_info["is_active"] or not agent_info["session_string"]:
                logger.warning("Agent is not active or has no session",
                             tenant_id=tenant_id,
                             agent_id=agent_id,
                             is_active=agent_info["is_active"],
                             has_session=bool(agent_info["session_string"]))
                return False
                
            # 세션 정보 구성
            session_info = {
                "tenant_id": agent_info["tenant_id"],
                "agent_id": agent_info["id"],
                "phone_number": agent_info["phone_number"],
                "name": agent_info["name"],
                "api_id": agent_info["api_id"],
                "api_hash": agent_info["api_hash"],
                "session_string": agent_info["session_string"]
            }
            
            # 클라이언트 생성
            await self._create_client(session_info)
            
            logger.info("Agent added to worker",
                       tenant_id=tenant_id,
                       agent_id=agent_id,
                       agent_name=agent_info["name"])
            return True
            
        except Exception as e:
            logger.error("Failed to add agent",
                        tenant_id=tenant_id,
                        agent_id=agent_id,
                        error=str(e))
            return False
            
    async def remove_agent(self, tenant_id: str, agent_id: str):
        """에이전트 제거"""
        client_key = f"{tenant_id}:{agent_id}"
        if client_key in self.clients:
            client = self.clients[client_key]
            if client.is_connected():
                await client.disconnect()
            del self.clients[client_key]
            
            # 관련 컨텍스트 캐시 정리
            keys_to_remove = [k for k in self.context_cache.keys() if k.startswith(f"{tenant_id}:{agent_id}:")]
            for key in keys_to_remove:
                del self.context_cache[key]
                
            logger.info("Agent removed from worker",
                       tenant_id=tenant_id,
                       agent_id=agent_id)
            return True
        return False
        
    async def _get_chat_config(self, tenant_id: str, agent_id: str, chat_id: int) -> Optional[Dict]:
        """agent_chat_configs에서 채팅 설정 조회"""
        try:
            client = supabase_service._get_supabase_client()
            
            # agent_chat_configs 테이블에서 조회
            result = client.table("agent_chat_configs").select(
                "persona_id, role, delay_seconds"
            ).eq("agent_id", agent_id).eq("chat_id", str(chat_id)).execute()
            
            if result.data:
                config = result.data[0]
                return {
                    "persona_id": config["persona_id"],
                    "role": config["role"],
                    "delay": config["delay_seconds"]
                }
            return None
            
        except Exception as e:
            logger.error(f"Chat config 조회 실패: {e}")
            return None
            
    async def _get_persona(self, tenant_id: str, persona_id: str) -> Optional[Dict]:
        """personas 테이블에서 페르소나 조회"""
        try:
            client = supabase_service._get_supabase_client()
            
            result = client.table("personas").select(
                "id, name, system_prompt"
            ).eq("id", persona_id).eq("tenant_id", tenant_id).execute()
            
            if result.data:
                persona = result.data[0]
                return {
                    "id": persona["id"],
                    "name": persona["name"],
                    "system_prompt": persona["system_prompt"]
                }
            return None
            
        except Exception as e:
            logger.error(f"Persona 조회 실패: {e}")
            return None

# 전역 워커 인스턴스
worker = TelegramWorker() 