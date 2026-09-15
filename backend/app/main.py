from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.api import routes, trades, market
from app.services.bot_runner import bot_runner_instance
from app.config import settings

# Create DB tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[APP] Trading Bot API initializing...")
    yield
    print("[APP] Shutting down Trading Bot background runner...")
    bot_runner_instance.stop()

app = FastAPI(
    title="Apex Real-Money & Paper Trading Bot API",
    description="Institutional-grade automated trading system & backtester API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")
app.include_router(trades.router, prefix="/api")
app.include_router(market.router, prefix="/api")

@app.get("/")
def root():
    return {
        "name": "Apex Trading Bot API",
        "status": "online",
        "mode": settings.MODE,
        "emergency_stop": settings.EMERGENCY_STOP,
        "notice": "MODE=PAPER — SIMULATION MODE ACTIVE" if settings.MODE == "PAPER" else "MODE=LIVE — REAL MONEY TRADING ACTIVE",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
