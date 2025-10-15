"""
Modèles Pydantic pour les runs de backtest
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class RunRequest(BaseModel):
    """Requête pour créer un run"""
    strategy_id: str
    parameters: Dict[str, Any] = {}
    name: Optional[str] = None  # Nom optionnel du backtest


class RunResponse(BaseModel):
    """Réponse après création d'un run"""
    run_id: str
    status: str
    message: str
    name: Optional[str] = None
    started_at: Optional[str] = None


class RunStatus(BaseModel):
    """Statut d'un run"""
    run_id: str
    status: str  # running | completed | failed
    progress: float = 0.0
    message: str = ""
    name: Optional[str] = None
    logs: List[str] = []
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class RunInfo(BaseModel):
    """Informations d'un run"""
    run_id: str
    status: str
    message: str
    name: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None


class RunListResponse(BaseModel):
    """Réponse pour la liste des runs"""
    runs: List[RunInfo]
    total: int


class RunMetrics(BaseModel):
    """Métriques d'un backtest"""
    total_trades: int
    win_rate: float
    net_pnl: float
    profit_factor: float
    max_drawdown: float
    avg_win: float
    avg_loss: float
    expectancy: float
    winning_trades: int
    losing_trades: int
    gross_profit: float
    gross_loss: float


class Trade(BaseModel):
    """Détails d'un trade"""
    id: int
    date: str
    entry_time: str
    exit_time: str
    direction: str
    entry: float
    exit: float
    points: float
    pnl_usd: float
    result: str


class RunResults(BaseModel):
    """Résultats complets d'un run"""
    run_id: str
    strategy: str
    metrics: RunMetrics
    equity_curve: List[float]
    drawdown_curve: List[float]
    trades: List[Trade] = []
    files: List[str] = []
