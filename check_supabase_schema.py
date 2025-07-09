import os
from dotenv import load_dotenv
from supabase import create_client

# .env 파일 로드
load_dotenv()

# Supabase 클라이언트 생성
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Supabase 환경변수가 설정되지 않았습니다")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

print("=== Supabase 스키마 확인 ===")

try:
    # 모든 테이블 조회
    print("\n1. 모든 테이블 목록:")
    result = supabase.table("information_schema.tables").select("table_name").eq("table_schema", "public").execute()
    
    for table in result.data:
        print(f"  - {table['table_name']}")
    
    # agent_sessions 테이블 구조 확인
    print("\n2. agent_sessions 테이블 구조:")
    try:
        result = supabase.table("agent_sessions").select("*").limit(1).execute()
        if result.data:
            print("  ✅ agent_sessions 테이블이 존재합니다")
            print(f"  컬럼: {list(result.data[0].keys())}")
        else:
            print("  ⚠️ agent_sessions 테이블이 비어있습니다")
    except Exception as e:
        print(f"  ❌ agent_sessions 테이블 오류: {e}")
    
    # agents 테이블 구조 확인
    print("\n3. agents 테이블 구조:")
    try:
        result = supabase.table("agents").select("*").limit(1).execute()
        if result.data:
            print("  ✅ agents 테이블이 존재합니다")
            print(f"  컬럼: {list(result.data[0].keys())}")
        else:
            print("  ⚠️ agents 테이블이 비어있습니다")
    except Exception as e:
        print(f"  ❌ agents 테이블 오류: {e}")
    
    # agent_chat_configs 테이블 구조 확인
    print("\n4. agent_chat_configs 테이블 구조:")
    try:
        result = supabase.table("agent_chat_configs").select("*").limit(1).execute()
        if result.data:
            print("  ✅ agent_chat_configs 테이블이 존재합니다")
            print(f"  컬럼: {list(result.data[0].keys())}")
        else:
            print("  ⚠️ agent_chat_configs 테이블이 비어있습니다")
    except Exception as e:
        print(f"  ❌ agent_chat_configs 테이블 오류: {e}")
    
    # 외래키 관계 확인
    print("\n5. 외래키 관계 확인:")
    try:
        result = supabase.table("information_schema.key_column_usage").select(
            "table_name,column_name,referenced_table_name,referenced_column_name"
        ).eq("table_schema", "public").execute()
        
        for relation in result.data:
            if relation.get('referenced_table_name'):
                print(f"  {relation['table_name']}.{relation['column_name']} -> {relation['referenced_table_name']}.{relation['referenced_column_name']}")
    except Exception as e:
        print(f"  ❌ 외래키 관계 확인 오류: {e}")
        
except Exception as e:
    print(f"❌ 스키마 확인 중 오류 발생: {e}") 