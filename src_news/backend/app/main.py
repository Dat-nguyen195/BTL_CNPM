from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.routers import auth, hubs, bookings, personal_ev, operations

app = FastAPI(title="Smart E-Mobility Hub API", version="2.0.0")

# 1. Rate Limiting chống Brute-force
app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. CORS chặt chẽ chỉ cho phép Frontend Domain
origins = [o.strip() for o in settings.FRONTEND_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# 3. Security Headers Middleware (Chống Clickjacking, XSS, MIME Sniffing)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.include_router(auth.router)
app.include_router(hubs.router)
app.include_router(bookings.router)
app.include_router(personal_ev.router)
app.include_router(operations.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}