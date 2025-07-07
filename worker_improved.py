#!/usr/bin/env python3
"""
개선된 텔레그램 워커 스크립트
실시간으로 텔레그램 메시지를 감지하고 AI 응답을 생성합니다.
"""

import asyncio
import signal
import sys
from app.services.worker_service import worker
from utils.logging import log

async def main():
    """메인 워커 함수"""
    log.info("Starting improved Telegram worker")
    
    try:
        # 워커 시작
        await worker.start_worker()
    except KeyboardInterrupt:
        log.info("Received interrupt signal, shutting down...")
    except Exception as e:
        log.error("Worker failed", error=str(e))
        raise
    finally:
        # 워커 정리
        await worker.stop_worker()
        log.info("Worker shutdown complete")

def signal_handler(signum, frame):
    """시그널 핸들러"""
    log.info(f"Received signal {signum}, initiating shutdown...")
    sys.exit(0)

if __name__ == "__main__":
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 워커 실행
    asyncio.run(main()) 