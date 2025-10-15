from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os
from pathlib import Path

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}
    run_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = {}
    
class DataAnalyst:
    """Expert en analyse de données de trading"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent / 'backend_runs'
        self.data_path = Path(__file__).parent.parent / 'data'
        
    def analyze_query(self, query: str, context: Dict[str, Any]) -> str:
        """Analyse la requête et génère une réponse appropriée"""
        query_lower = query.lower()
        
        # Analyse de performances
        if any(word in query_lower for word in ['performance', 'pnl', 'profit', 'loss', 'backtest']):
            return self._analyze_performance(context)
            
        # Analyse de volatilité
        if any(word in query_lower for word in ['volatilité', 'volatility', 'vol', 'risk']):
            return self._analyze_volatility()
            
        # Génération de code
        if any(word in query_lower for word in ['code', 'script', 'python', 'générer', 'sharpe', 'calmar']):
            return self._generate_code(query_lower)
            
        # Distribution temporelle
        if any(word in query_lower for word in ['heure', 'hour', 'temps', 'time', 'distribution']):
            return self._analyze_temporal()
            
        return self._default_response(query)
        
    def _analyze_performance(self, context: Dict[str, Any]) -> str:
        """Analyse les performances d'un backtest"""
        run_id = context.get('run_id')
        if not run_id:
            return self._get_latest_run_performance()
            
        try:
            run_path = self.base_path / run_id
            if not run_path.exists():
                return "❌ Run non trouvé. Vérifiez l'ID du backtest."
                
            trades_file = run_path / 'trades.csv'
            if trades_file.exists():
                trades_df = pd.read_csv(trades_file)
                
                total_trades = len(trades_df)
                if total_trades == 0:
                    return "📊 Aucun trade dans ce backtest."
                    
                winning_trades = len(trades_df[trades_df['pnl'] > 0])
                win_rate = (winning_trades / total_trades) * 100
                total_pnl = trades_df['pnl'].sum()
                avg_pnl = trades_df['pnl'].mean()
                max_win = trades_df['pnl'].max()
                max_loss = trades_df['pnl'].min()
                
                cumulative_pnl = trades_df['pnl'].cumsum()
                running_max = cumulative_pnl.expanding().max()
                drawdown = (cumulative_pnl - running_max)
                max_drawdown = drawdown.min()
                
                if trades_df['pnl'].std() > 0:
                    sharpe = (avg_pnl / trades_df['pnl'].std()) * np.sqrt(252)
                else:
                    sharpe = 0
                    
                return f"""## 📊 Analyse des Performances - Run {run_id[:8]}

### 📈 Métriques Principales
- **Total Trades**: {total_trades}
- **Win Rate**: {win_rate:.1f}% ({winning_trades}W / {total_trades - winning_trades}L)
- **PnL Total**: ${total_pnl:,.2f}
- **PnL Moyen**: ${avg_pnl:,.2f}

### 💰 Distribution des Gains
- **Plus Gros Gain**: ${max_win:,.2f}
- **Plus Grosse Perte**: ${max_loss:,.2f}

### 📉 Gestion du Risque
- **Max Drawdown**: ${max_drawdown:,.2f}
- **Sharpe Ratio**: {sharpe:.2f}"""
                
        except Exception as e:
            return f"❌ Erreur lors de l'analyse: {str(e)}"
            
    def _get_latest_run_performance(self) -> str:
        """Récupère les performances du dernier run"""
        try:
            runs = [d for d in self.base_path.iterdir() if d.is_dir()]
            if not runs:
                return "📊 Aucun backtest trouvé. Lancez un backtest d'abord."
                
            latest_run = max(runs, key=lambda x: x.stat().st_mtime)
            run_id = latest_run.name
            return self._analyze_performance({'run_id': run_id})
            
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
            
    def _analyze_volatility(self) -> str:
        """Analyse la volatilité des données"""
        return """## 📈 Analyse de Volatilité

### Code d'Analyse
```python
import pandas as pd
import numpy as np

# Chargement des données OHLCV
df = pd.read_csv('data/ohlcv.csv')
df['returns'] = df['close'].pct_change()

# Volatilité historique (20 périodes)
df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)

# Statistiques
current_vol = df['volatility'].iloc[-1]
avg_vol = df['volatility'].mean()

print(f"Volatilité actuelle: {current_vol:.2%}")
print(f"Volatilité moyenne: {avg_vol:.2%}")
```

### 📊 Interprétation
- Volatilité élevée = opportunités + risques
- Adaptez vos positions selon la volatilité
- Surveillez les pics pour identifier les événements"""

    def _generate_code(self, query: str) -> str:
        """Génère du code Python selon la demande"""
        if 'sharpe' in query:
            return """## 💻 Code pour calculer le Sharpe Ratio

```python
import pandas as pd
import numpy as np

def calculate_sharpe_ratio(returns, risk_free_rate=0.02, periods=252):
    excess_returns = returns - (risk_free_rate / periods)
    if returns.std() == 0:
        return 0
    sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(periods)
    return sharpe

# Utilisation
df = pd.read_csv('trades.csv')
df['returns'] = df['pnl'] / 50000  # Capital initial
sharpe = calculate_sharpe_ratio(df['returns'])
print(f"Sharpe Ratio: {sharpe:.2f}")
```

### Interprétation
- **> 2.0**: Excellent
- **1.0-2.0**: Bon
- **< 1.0**: À améliorer"""
            
        elif 'calmar' in query:
            return """## 💻 Code pour calculer le Calmar Ratio

```python
def calculate_calmar_ratio(pnl_series):
    total_return = pnl_series.sum()
    cumulative = pnl_series.cumsum()
    running_max = cumulative.expanding().max()
    drawdown = cumulative - running_max
    max_drawdown = abs(drawdown.min())
    
    if max_drawdown == 0:
        return float('inf')
    
    calmar = total_return / max_drawdown
    return calmar

df = pd.read_csv('trades.csv')
calmar = calculate_calmar_ratio(df['pnl'])
print(f"Calmar Ratio: {calmar:.2f}")
```"""
        else:
            return """## 💻 Framework d'Analyse Complet

```python
import pandas as pd
import numpy as np

class BacktestAnalyzer:
    def __init__(self, trades_file='trades.csv'):
        self.df = pd.read_csv(trades_file)
        
    def compute_metrics(self):
        metrics = {
            'total_trades': len(self.df),
            'win_rate': (self.df['pnl'] > 0).mean(),
            'avg_pnl': self.df['pnl'].mean(),
            'total_pnl': self.df['pnl'].sum(),
            'sharpe': self._calculate_sharpe()
        }
        return metrics
    
    def _calculate_sharpe(self):
        if self.df['pnl'].std() > 0:
            return (self.df['pnl'].mean() / self.df['pnl'].std()) * np.sqrt(252)
        return 0

analyzer = BacktestAnalyzer()
print(analyzer.compute_metrics())
```"""

    def _analyze_temporal(self) -> str:
        """Analyse la distribution temporelle"""
        return """## ⏰ Distribution Temporelle

### Code d'Analyse
```python
df = pd.read_csv('trades.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour

hourly_stats = df.groupby('hour')['pnl'].agg(['sum', 'mean', 'count'])
best_hour = hourly_stats['sum'].idxmax()
worst_hour = hourly_stats['sum'].idxmin()

print(f"Meilleure heure: {best_hour}h UTC")
print(f"Pire heure: {worst_hour}h UTC")
```

### Insights
- **14h-16h UTC**: Haute volatilité (ouverture US)
- **17h-19h UTC**: Session calme
- **Focus**: Heures avec meilleur risk/reward"""
            
    def _default_response(self, query: str) -> str:
        """Réponse par défaut"""
        return f"""## 🔍 Analyse en cours...

Je traite votre requête: "{query}"

Essayez des questions spécifiques comme:
- "Analyse les performances du dernier backtest"
- "Génère un code pour calculer le Sharpe ratio"
- "Montre la distribution temporelle des trades"
- "Analyse la volatilité récente"

Je suis là pour vous aider à comprendre vos données de trading!"""

# Initialisation de l'analyseur
analyst = DataAnalyst()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_analyst(request: ChatRequest):
    """Endpoint pour le chat avec l'IA analyst"""
    try:
        response = analyst.analyze_query(request.message, request.context or {})
        return ChatResponse(
            response=response,
            metadata={"timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs")
async def get_available_runs():
    """Récupère la liste des runs disponibles"""
    try:
        base_path = Path(__file__).parent.parent.parent / 'backend_runs'
        runs = []
        
        for run_dir in base_path.iterdir():
            if run_dir.is_dir():
                config_file = run_dir / 'config.json'
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    runs.append({
                        'run_id': run_dir.name,
                        'strategy': config.get('strategy', 'Unknown'),
                        'timestamp': datetime.fromtimestamp(run_dir.stat().st_mtime).isoformat(),
                        'status': 'completed' if (run_dir / 'trades.csv').exists() else 'incomplete'
                    })
        
        return {"runs": sorted(runs, key=lambda x: x['timestamp'], reverse=True)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/run/{run_id}/summary")
async def get_run_summary(run_id: str):
    """Récupère le résumé d'un run spécifique"""
    try:
        response = analyst.analyze_performance({'run_id': run_id})
        return {"run_id": run_id, "summary": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
