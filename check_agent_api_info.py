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

async def check_agent_api_info():
    """에이전트별 API 정보 확인"""
    try:
        # agents 테이블에서 API 정보 조회
        result = supabase.table("agents").select(
            "id, name, api_id, api_hash, phone_number, is_active"
        ).execute()
        
        print("=== 에이전트별 API 정보 ===")
        for agent in result.data:
            print(f"에이전트 ID: {agent.get('id')}")
            print(f"이름: {agent.get('name')}")
            print(f"API ID: {agent.get('api_id')} (타입: {type(agent.get('api_id'))})")
            print(f"API Hash: {agent.get('api_hash')} (타입: {type(agent.get('api_hash'))})")
            print(f"전화번호: {agent.get('phone_number')}")
            print(f"활성화: {agent.get('is_active')}")
            print("---")
            
        # 활성 에이전트만 필터링
        active_agents = [a for a in result.data if a.get('is_active')]
        print(f"\n활성 에이전트 수: {len(active_agents)}")
        
        # API 정보 유효성 검사
        for agent in active_agents:
            api_id = agent.get('api_id')
            api_hash = agent.get('api_hash')
            
            if api_id and api_hash:
                print(f"✅ {agent.get('name')}: API 정보 있음")
            else:
                print(f"❌ {agent.get('name')}: API 정보 없음")
                
    except Exception as e:
        print(f"에러: {e}")

if __name__ == "__main__":
    asyncio.run(check_agent_api_info()) 