from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth_router import router as auth_router
from utils.logging import log

app = FastAPI(title="Telegram Auth API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=False,  # credentials가 false일 때만 * 허용 가능
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
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
