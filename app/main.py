from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth_router import router as auth_router
from app.routers.persona_router import router as persona_router
from app.routers.mapping_router import router as map_router
from app.routers.agent_router import router as agent_router
from utils.logging import log
from app.config import settings

app = FastAPI(title="Telegram Auth API")

ALLOWED_ORIGINS = [
    "https://v0-supabase-community-starter-qb.vercel.app",
    "https://v0-supabase-community-starter-jo-kappa.vercel.app",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(persona_router)
app.include_router(map_router)
app.include_router(agent_router)

@app.get("/healthz")
async def health():
    return {"status": "ok"}

@app.get("/debug/env")
async def debug_env():
    """환경변수 디버깅용 엔드포인트"""
    return {
        "openai_api_key_set": bool(settings.openai_api_key),
        "supabase_url_set": bool(settings.supabase_url),
        "supabase_key_set": bool(settings.supabase_key),
        "supabase_url_length": len(settings.supabase_url) if settings.supabase_url else 0,
        "supabase_key_length": len(settings.supabase_key) if settings.supabase_key else 0,
        "supabase_url_start": settings.supabase_url[:20] + "..." if settings.supabase_url and len(settings.supabase_url) > 20 else settings.supabase_url,
        "supabase_key_start": settings.supabase_key[:20] + "..." if settings.supabase_key and len(settings.supabase_key) > 20 else settings.supabase_key,
    }

@app.on_event("startup")
async def startup():
    log.info("startup")

@app.on_event("shutdown")
async def shutdown():
    log.info("shutdown")

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
