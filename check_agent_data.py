import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

# 환경 변수 로드
load_dotenv()

# Supabase 클라이언트 생성
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

async def check_agent_data():
    """에이전트 데이터 구조 확인"""
    try:
        # agents 테이블에서 데이터 조회
        result = supabase.table("agents").select("*").limit(5).execute()
        
        print("=== Agents 테이블 데이터 ===")
        for agent in result.data:
            print(f"ID: {agent.get('id')}")
            print(f"Name: {agent.get('name')}")
            print(f"API ID: {agent.get('api_id')} (Type: {type(agent.get('api_id'))})")
            print(f"API Hash: {agent.get('api_hash')} (Type: {type(agent.get('api_hash'))})")
            print(f"Phone: {agent.get('phone_number')}")
            print(f"Session: {agent.get('session_string')[:50] if agent.get('session_string') else 'None'}...")
            print(f"Is Active: {agent.get('is_active')}")
            print("---")
            
    except Exception as e:
        print(f"에러: {e}")

if __name__ == "__main__":
    asyncio.run(check_agent_data()) 