import asyncio
import aiohttp
from aiohttp import web
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_handler(request):
    """헬스체크 엔드포인트"""
    return web.json_response({
        "status": "healthy",
        "service": "telegram-worker",
        "timestamp": asyncio.get_event_loop().time()
    })

async def start_health_server():
    """헬스체크 서버 시작"""
    app = web.Application()
    app.router.add_get('/health', health_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    logger.info("Health check server started on port 8080")
    return runner

if __name__ == "__main__":
    asyncio.run(start_health_server()) 