import asyncio
import os
import signal
import sys
from dotenv import load_dotenv
from app.services.worker_service import worker
from worker_health import start_health_server

# 환경 변수 로드
load_dotenv()

async def main():
    """메인 워커 함수"""
    # 헬스체크 서버 시작
    health_runner = await start_health_server()
    
    try:
        # 워커 시작
        await worker.start_worker()
        
        # 무한 대기
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 워커 종료 중...")
    except Exception as e:
        print(f"❌ 워커 에러: {e}")
    finally:
        # 정리 작업
        await worker.stop_worker()
        await health_runner.cleanup()
        print("✅ 워커 종료 완료")

def signal_handler(signum, frame):
    """시그널 핸들러"""
    print(f"\n📡 시그널 {signum} 수신, 워커 종료 중...")
    sys.exit(0)

if __name__ == "__main__":
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 운영 환경 워커 시작...")
    asyncio.run(main()) 