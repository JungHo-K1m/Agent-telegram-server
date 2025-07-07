import asyncio
import os
from typing import Dict, List, Optional, Any
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import structlog

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
        """모든 테넌트의 활성 세션 조회"""
        client = supabase_service._get_supabase_client()
        
        # 모든 활성 세션 조회 (테넌트 정보 포함)
        result = client.table("agent_sessions").select(
            "agent_id, session_string, agents!inner(tenant_id, id, name, api_id, api_hash, phone_number)"
        ).eq("is_active", True).execute()
        
        sessions = []
        for session in result.data:
            agent_info = session["agents"]
            sessions.append({
                "tenant_id": agent_info["tenant_id"],
                "agent_id": agent_info["id"],
                "phone_number": agent_info["phone_number"],
                "name": agent_info["name"],
                "api_id": agent_info["api_id"],
                "api_hash": agent_info["api_hash"],
                "session_string": session["session_string"]
            })
            
        return sessions
        
    async def _create_client(self, session_info: Dict):
        """텔레그램 클라이언트 생성 및 이벤트 핸들러 설정"""
        try:
            client = TelegramClient(
                StringSession(session_info["session_string"]),
                session_info["api_id"],
                session_info["api_hash"]
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
            
            # 매핑 정보 조회
            mapping = supabase_service.get_mapping(tenant_id, agent_id, chat_id)
            if not mapping:
                logger.debug("No mapping found for chat", 
                           tenant_id=tenant_id,
                           agent_id=agent_id,
                           chat_id=chat_id)
                return
                
            # 페르소나 정보 조회
            persona = supabase_service.get_persona(tenant_id, mapping["persona_id"])
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
            # 에이전트 세션 정보 조회
            session_info = supabase_service.get_agent_session_with_tenant(tenant_id, agent_id)
            if not session_info or not session_info["is_active"]:
                logger.warning("No active session found for agent",
                             tenant_id=tenant_id,
                             agent_id=agent_id)
                return False
                
            # 에이전트 정보 조회
            agent_info = supabase_service.get_agent(tenant_id, agent_id)
            if not agent_info:
                logger.warning("Agent not found",
                             tenant_id=tenant_id,
                             agent_id=agent_id)
                return False
                
            # 세션 정보에 에이전트 정보 추가
            full_session_info = {
                "tenant_id": tenant_id,
                "agent_id": agent_id,
                "phone_number": agent_info["phone_number"],
                "name": agent_info["name"],
                "api_id": agent_info["api_id"],
                "api_hash": agent_info["api_hash"],
                "session_string": session_info["session_string"]
            }
            
            # 클라이언트 생성
            await self._create_client(full_session_info)
            
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

# 전역 워커 인스턴스
worker = TelegramWorker() 