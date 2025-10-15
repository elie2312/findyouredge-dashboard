"""
Router pour les stratégies de backtest
Utilise le système de découverte existant
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import sys
from models.strategy import StrategyListResponse, Strategy

# Chemins vers les services backend
BACKEND_PATH = Path(__file__).parent.parent
BACKTEST_SERVICE_PATH = BACKEND_PATH / "services" / "backtest"
sys.path.insert(0, str(BACKTEST_SERVICE_PATH))

try:
    from discover import get_available_strategies
except ImportError as e:
    print(f"Erreur import discover: {e}")
    get_available_strategies = None

router = APIRouter()


@router.get("", response_model=StrategyListResponse)
def list_strategies():
    """
    Récupère la liste des stratégies disponibles
    Utilise le système de découverte existant
    """
    if get_available_strategies is None:
        raise HTTPException(
            status_code=500, 
            detail="Module discover non disponible"
        )
    
    try:
        # Utiliser la fonction de découverte avec le nouveau chemin
        strategies_raw = get_available_strategies(str(BACKEND_PATH))
        
        # Convertir au format API
        strategies = []
        for s in strategies_raw:
            strategy = Strategy(
                id=s['name'].lower().replace(' ', '_').replace('-', '_'),
                name=s['name'],
                description=s['description'],
                timeframe=s['timeframe'],
                risk_model=s['risk_model'],
                parameters=s['parameters'],
                script_path=s['script_path'],
                category=s.get('category', 'Autres'),
                tags=s.get('tags', [])
            )
            strategies.append(strategy)
        
        return StrategyListResponse(strategies=strategies)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la découverte des stratégies: {str(e)}"
        )


@router.get("/{strategy_id}")
def get_strategy(strategy_id: str):
    """
    Récupère les détails d'une stratégie spécifique
    """
    strategies_response = list_strategies()
    
    for strategy in strategies_response.strategies:
        if strategy.id == strategy_id:
            return strategy
    
    raise HTTPException(
        status_code=404,
        detail=f"Stratégie {strategy_id} non trouvée"
    )
