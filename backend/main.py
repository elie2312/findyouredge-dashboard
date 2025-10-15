"""
FastAPI Backend pour NQ Backtest Dashboard
Point d'entrée principal de l'API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import strategies, runs, ai_analyst, ninja_strategies

app = FastAPI(
    title="NQ Backtest API",
    description="API pour lancer et monitorer des backtests NQ",
    version="1.0.0"
)

# Configuration CORS pour Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
app.include_router(ai_analyst.router, prefix="/api/ai", tags=["ai_analyst"])
app.include_router(ninja_strategies.router, prefix="/api/ninja-strategies", tags=["ninja_strategies"])

@app.get("/")
def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "NQ Backtest API",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health():
    """Health check détaillé"""
    return {
        "status": "healthy",
        "endpoints": {
            "strategies": "/api/strategies",
            "runs": "/api/runs",
            "docs": "/docs"
        }
    }
