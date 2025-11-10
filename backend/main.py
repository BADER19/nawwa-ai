import os
import time
from sqlalchemy import text
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
try:
    from dotenv import load_dotenv
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidates = [
        os.path.join(base_dir, ".env"),
        os.path.join(base_dir, "infra", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
    ]
    for p in candidates:
        if os.path.exists(p):
            load_dotenv(p, override=False)
except Exception:
    pass

from services import auth as auth_service
from services import visualize as visualize_service
from services import workspace as workspace_service
from services import project as project_service
from services import math_visualize as math_visualize_service
from services import image_proxy_router as image_proxy_service
from services import subscription_router as subscription_service
from services import paypal_webhook as paypal_webhook_service
from services import chat as chat_service
from services import voice as voice_service
from services import admin as admin_service
from engines.math_interactive import api as math_interactive_service
from services.llm_service import llm_ready, MODEL as LLM_MODEL
from services.image_service import can_generate_images, IMAGE_MODEL as IMG_MODEL
from services.config import AI_IMAGE_FIRST, AI_DISABLE_RULES, AI_REQUIRE, TIER_MODELS
from services.db import engine
from services.redis_client import ping_redis
from models.base import Base


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Enforce HTTPS in production (commented for local dev)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy - Allow Swagger UI CDN for /docs endpoint
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            # Relaxed CSP for API documentation
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' data:;"
            )
        else:
            # Strict CSP for all other endpoints
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"

        return response


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


def create_app() -> FastAPI:
    app = FastAPI(title="Instant Visualization API", version="0.1.0")

    # Add rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # CORS configuration
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup():
        # Wait for Postgres to be ready
        max_attempts = 30
        for i in range(max_attempts):
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                break
            except Exception:
                time.sleep(1)
        # Create tables after DB is reachable
        Base.metadata.create_all(bind=engine)
        # Best-effort Redis ping
        ping_redis()

    @app.get("/health")
    def health():
        return {
            "ok": True,
            "llm_ready": llm_ready(),
            "image_ready": can_generate_images(),
            "model": LLM_MODEL,
            "image_model": IMG_MODEL,
            "flags": {
                "image_first": AI_IMAGE_FIRST,
                "disable_rules": AI_DISABLE_RULES,
                "require_ai": AI_REQUIRE,
            },
            "tier_models": {
                tier: {
                    "model": config["llm_model"],
                    "images": config["enable_images"],
                    "voice": config["enable_voice"]
                }
                for tier, config in TIER_MODELS.items()
            }
        }

    @app.get("/debug/env")
    def debug_env():
        """Debug endpoint to check environment variables (remove in production)"""
        import os
        return {
            "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
            "key_length": len(os.getenv("OPENAI_API_KEY", "")) if os.getenv("OPENAI_API_KEY") else 0,
            "key_prefix": os.getenv("OPENAI_API_KEY", "")[:10] + "..." if os.getenv("OPENAI_API_KEY") else None,
            "all_env_keys": sorted([k for k in os.environ.keys() if not k.startswith("_")]),
            "cors_origins": os.getenv("CORS_ORIGINS"),
            "database_url_exists": bool(os.getenv("DATABASE_URL")),
            "redis_url_exists": bool(os.getenv("REDIS_URL")),
        }

    app.include_router(auth_service.router, prefix="/auth", tags=["auth"])
    app.include_router(visualize_service.router, prefix="/visualize", tags=["visualize"])
    app.include_router(voice_service.router, prefix="/visualize", tags=["voice"])
    app.include_router(math_visualize_service.router, tags=["math"])
    app.include_router(math_interactive_service.router, tags=["math_interactive"])
    app.include_router(workspace_service.router, prefix="/workspace", tags=["workspace"])
    app.include_router(project_service.router, tags=["projects"])
    app.include_router(image_proxy_service.router, prefix="/image", tags=["image"])
    app.include_router(subscription_service.router, prefix="/subscription", tags=["subscription"])
    app.include_router(paypal_webhook_service.router, tags=["paypal"])
    app.include_router(chat_service.router, prefix="/chat", tags=["chat"])
    app.include_router(admin_service.router, prefix="/admin", tags=["admin"])

    # Dashboard routes - temporarily disabled
    # from services import dashboard as dashboard_service
    # app.include_router(dashboard_service.router, prefix="/dashboard", tags=["dashboard"])

    return app


app = create_app()
