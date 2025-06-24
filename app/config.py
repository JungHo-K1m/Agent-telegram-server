import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # 기본값을 없애거나 None 허용으로 두면, 요청에서 반드시 받아야 함
    API_ID: Optional[int] = None
    API_HASH: Optional[str] = None

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    
    # Telegram (기본값, 실제로는 accounts 테이블에서 관리)
    telegram_api_id: int = int(os.getenv("API_ID", "0"))
    telegram_api_hash: str = os.getenv("API_HASH", "")

    model_config: SettingsConfigDict = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()
