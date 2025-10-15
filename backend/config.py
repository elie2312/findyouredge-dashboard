"""
Configuration centralisée pour le backend
Charge les variables depuis .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# Chemin vers les données de marché
DATA_CSV_PATH = os.getenv("DATA_CSV_PATH", "data/raw/glbx-mdp3-20240814-20250813.ohlcv-1s.csv")
DATA_CSV_FULL_PATH = BASE_DIR / DATA_CSV_PATH

# Dossier de sortie des runs
RUNS_DIR = BASE_DIR / os.getenv("RUNS_DIR", "runs")

# Configuration API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS Origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

# Validation
if not DATA_CSV_FULL_PATH.exists():
    print(f"⚠️  ATTENTION: Le fichier de données n'existe pas: {DATA_CSV_FULL_PATH}")
    print(f"   Vérifiez la variable DATA_CSV_PATH dans .env")

# Export pour faciliter l'import
__all__ = [
    "DATA_CSV_PATH",
    "DATA_CSV_FULL_PATH",
    "RUNS_DIR",
    "API_HOST",
    "API_PORT",
    "CORS_ORIGINS",
    "BASE_DIR"
]
