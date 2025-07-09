import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

print("=== 환경변수 확인 ===")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NOT_SET')}")
print(f"SUPABASE_SERVICE_ROLE_KEY: {os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'NOT_SET')}")
print(f"SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY', 'NOT_SET')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT_SET')}")

# .env 파일 존재 확인
import os.path
if os.path.exists('.env'):
    print("\n✅ .env 파일이 존재합니다")
    with open('.env', 'r') as f:
        print("=== .env 파일 내용 ===")
        for line in f:
            if line.strip() and not line.startswith('#'):
                print(line.strip())
else:
    print("\n❌ .env 파일이 존재하지 않습니다") 