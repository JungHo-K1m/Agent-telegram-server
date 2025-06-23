from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # 기본값을 없애거나 None 허용으로 두면, 요청에서 반드시 받아야 함
    API_ID: Optional[int] = None
    API_HASH: Optional[str] = None

    model_config: SettingsConfigDict = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()
