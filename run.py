#!/usr/bin/env python3
"""Launch the FastAPI application; migrations are run separately in production."""
import os

import uvicorn

from backend.config import APP_ENV, FORWARDED_ALLOW_IPS

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        reload=APP_ENV == "development" and os.getenv("RELOAD", "false").lower() == "true",
        proxy_headers=APP_ENV == "production",
        forwarded_allow_ips=FORWARDED_ALLOW_IPS,
        access_log=False,
    )
