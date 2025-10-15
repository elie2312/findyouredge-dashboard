"""
Modèles Pydantic pour les stratégies
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class Strategy(BaseModel):
    """Modèle d'une stratégie de backtest"""
    id: str
    name: str
    description: str
    timeframe: str
    risk_model: str
    parameters: Dict[str, Any]
    script_path: str
    category: str
    tags: List[str]


class StrategyListResponse(BaseModel):
    """Réponse pour la liste des stratégies"""
    strategies: list[Strategy]
