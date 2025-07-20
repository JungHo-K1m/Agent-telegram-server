#!/usr/bin/env python3
"""
Railway 서버 시작 스크립트
환경변수 PORT를 안전하게 처리
"""

import os
import uvicorn

if __name__ == "__main__":
    # 포트 설정 (환경변수에서 가져오거나 기본값 사용)
    port = int(os.environ.get("PORT", 8080))
    
    # 서버 시작
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 