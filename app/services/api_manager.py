import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TelegramAPIManager:
    """다중 Telegram API 계정 관리"""
    
    def __init__(self):
        self.api_accounts = {}
        self._load_api_accounts()
    
    def _load_api_accounts(self):
        """환경 변수에서 API 계정들 로드"""
        # 기본 API 계정
        default_api_id = os.getenv("TELEGRAM_API_ID", "25060740")
        default_api_hash = os.getenv("TELEGRAM_API_HASH", "f93d24a5fba99007d0a81a28ab5ca7bc")
        
        self.api_accounts["default"] = {
            "api_id": int(default_api_id),
            "api_hash": default_api_hash,
            "name": "Default API"
        }
        
        # 추가 API 계정들 (선택사항)
        # TELEGRAM_API_ID_2, TELEGRAM_API_HASH_2 등으로 설정 가능
        for i in range(2, 11):  # 최대 10개 API 계정 지원
            api_id = os.getenv(f"TELEGRAM_API_ID_{i}")
            api_hash = os.getenv(f"TELEGRAM_API_HASH_{i}")
            
            if api_id and api_hash:
                self.api_accounts[f"api_{i}"] = {
                    "api_id": int(api_id),
                    "api_hash": api_hash,
                    "name": f"API Account {i}"
                }
        
        logger.info(f"로드된 API 계정 수: {len(self.api_accounts)}")
    
    def get_api_info(self, account_name: str = "default") -> Optional[Dict]:
        """특정 API 계정 정보 반환"""
        return self.api_accounts.get(account_name)
    
    def get_all_api_accounts(self) -> Dict:
        """모든 API 계정 정보 반환"""
        return self.api_accounts
    
    def add_api_account(self, name: str, api_id: int, api_hash: str):
        """새로운 API 계정 추가"""
        self.api_accounts[name] = {
            "api_id": api_id,
            "api_hash": api_hash,
            "name": name
        }
        logger.info(f"새로운 API 계정 추가: {name}")
    
    def remove_api_account(self, name: str):
        """API 계정 제거"""
        if name in self.api_accounts:
            del self.api_accounts[name]
            logger.info(f"API 계정 제거: {name}")
    
    def validate_api_account(self, api_id: int, api_hash: str) -> bool:
        """API 계정 유효성 검사"""
        try:
            from telethon import TelegramClient
            from telethon.sessions import StringSession
            
            # 간단한 연결 테스트
            client = TelegramClient(StringSession(""), api_id, api_hash)
            return True
        except Exception as e:
            logger.error(f"API 계정 유효성 검사 실패: {e}")
            return False

# 전역 인스턴스
api_manager = TelegramAPIManager() 