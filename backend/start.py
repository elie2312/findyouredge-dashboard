"""
Script de démarrage du backend FastAPI
Usage: python start.py
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Démarrage du backend NQ Backtest API...")
    print("📡 API disponible sur: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("❌ Arrêt: Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Désactivé pour éviter d'interrompre les backtests
        log_level="info"
    )
