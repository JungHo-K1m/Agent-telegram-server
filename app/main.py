from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth_router import router as auth_router
from utils.logging import log

app = FastAPI(title="Telegram Auth API")

ALLOWED_ORIGINS = [
    "https://v0-supabase-community-starter-qb.vercel.app/",
    "http://localhost:8000",          # 개발용
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 개발 중 전체 허용
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/healthz")
async def health():
    return {"status": "ok"}

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
