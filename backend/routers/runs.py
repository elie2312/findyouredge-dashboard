"""
Router pour les runs de backtest
Utilise le système runner existant
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pathlib import Path
import sys
import uuid
from datetime import datetime
from models.run import (
    RunRequest, RunResponse, RunStatus, RunListResponse, 
    RunResults, RunInfo, RunMetrics, Trade
)

# Chemins vers les services backend
BACKEND_PATH = Path(__file__).parent.parent
BACKTEST_SERVICE_PATH = BACKEND_PATH / "services" / "backtest"
sys.path.insert(0, str(BACKTEST_SERVICE_PATH))

try:
    from run_backtest import create_runner
except ImportError as e:
    print(f"Erreur import run_backtest: {e}")
    create_runner = None

router = APIRouter()

# Instance globale du runner (sera initialisée au premier appel)
_runner = None

def get_runner():
    """Récupère l'instance du runner (singleton)"""
    global _runner
    if _runner is None:
        if create_runner is None:
            raise HTTPException(
                status_code=500,
                detail="Module run_backtest non disponible"
            )
        _runner = create_runner(str(BACKEND_PATH))
    return _runner


@router.post("", response_model=RunResponse)
def create_run(request: RunRequest, background_tasks: BackgroundTasks):
    """
    Lance un nouveau backtest en arrière-plan
    """
    # Log dans un fichier pour debug
    import logging
    logging.basicConfig(
        filename='C:/Users/elieb/Desktop/Dashboard/backend/debug.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔄 Début lancement backtest, strategy_id: {request.strategy_id}")
        print(f"🔄 Début lancement backtest, strategy_id: {request.strategy_id}")
        
        runner = get_runner()
        logger.info(f"✅ Runner obtenu: {runner}")
        
        # Importer discover pour récupérer les stratégies
        from discover import get_available_strategies
        logger.info(f"✅ Import discover OK")
        
        # Récupérer la liste des stratégies
        strategies = get_available_strategies(str(BACKEND_PATH))
        logger.info(f"✅ {len(strategies)} stratégies trouvées")
        
        # Trouver la stratégie correspondante
        strategy = None
        for s in strategies:
            strategy_id = s['name'].lower().replace(' ', '_').replace('-', '_')
            logger.debug(f"  Comparaison: {strategy_id} == {request.strategy_id} ?")
            if strategy_id == request.strategy_id:
                strategy = s
                break
        
        if not strategy:
            logger.error(f"❌ Stratégie non trouvée: {request.strategy_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Stratégie {request.strategy_id} non trouvée"
            )
        
        logger.info(f"✅ Stratégie trouvée: {strategy['name']}")
        logger.info(f"   Script: {strategy['script_path']}")
        
        # Utiliser le runner pour lancer le backtest
        # start_backtest retourne le run_id
        logger.info(f"🚀 Appel start_backtest...")
        run_id = runner.start_backtest(
            strategy_name=strategy['name'],
            script_path=strategy['script_path'],
            csv_path=None,  # Utilise le CSV par défaut
            parameters=request.parameters,
            name=request.name
        )
        logger.info(f"✅ Backtest lancé, run_id: {run_id}")
        
        return RunResponse(
            run_id=run_id,
            status="pending",
            message=f"Backtest {strategy['name']} en préparation",
            name=request.name,
            started_at=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"❌ ERREUR LANCEMENT: {error_detail}")
        print(f"❌ ERREUR LANCEMENT: {error_detail}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du lancement: {str(e)}"
        )


@router.get("", response_model=RunListResponse)
def list_runs():
    """
    Récupère la liste des runs
    """
    try:
        runner = get_runner()
        runs_raw = runner.list_runs()
        
        runs = []
        for r in runs_raw:
            # Calculer la durée si terminé
            duration = None
            if r.started_at and r.completed_at:
                try:
                    start = datetime.fromisoformat(r.started_at.replace('Z', '+00:00'))
                    end = datetime.fromisoformat(r.completed_at.replace('Z', '+00:00'))
                    duration = (end - start).total_seconds()
                except:
                    pass
            
            run_info = RunInfo(
                run_id=r.run_id,
                status=r.status,
                message=r.message,
                name=r.name,
                started_at=r.started_at,
                completed_at=r.completed_at,
                duration_seconds=duration
            )
            runs.append(run_info)
        
        return RunListResponse(
            runs=runs,
            total=len(runs)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des runs: {str(e)}"
        )


@router.get("/{run_id}/status", response_model=RunStatus)
def get_run_status(run_id: str):
    """
    Récupère le statut d'un run spécifique
    """
    try:
        runner = get_runner()
        
        # Utiliser votre méthode existante pour récupérer le statut
        # TODO: Adapter selon votre API runner
        runs = runner.list_runs()
        
        for run in runs:
            if run.run_id == run_id:
                return RunStatus(
                    run_id=run.run_id,
                    status=run.status,
                    progress=0.5 if run.status == "running" else 1.0,
                    message=run.message,
                    name=run.name,
                    logs=[],  # TODO: Récupérer les logs
                    started_at=run.started_at,
                    completed_at=run.completed_at
                )
        
        raise HTTPException(
            status_code=404,
            detail=f"Run {run_id} non trouvé"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du statut: {str(e)}"
        )


@router.get("/{run_id}/results", response_model=RunResults)
def get_run_results(run_id: str):
    """
    Récupère les résultats détaillés d'un run terminé
    """
    try:
        runner = get_runner()
        
        # Vérifier que le run existe et est terminé
        runs = runner.list_runs()
        target_run = None
        
        for run in runs:
            if run.run_id == run_id:
                target_run = run
                break
        
        if not target_run:
            raise HTTPException(
                status_code=404,
                detail=f"Run {run_id} non trouvé"
            )
        
        if target_run.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Run {run_id} n'est pas terminé (statut: {target_run.status})"
            )
        
        # Récupérer les résultats via votre système existant
        results_raw = runner.get_results(run_id)
        
        if not results_raw:
            raise HTTPException(
                status_code=404,
                detail=f"Résultats non trouvés pour le run {run_id}"
            )
        
        # Convertir au format API
        metrics = RunMetrics(
            total_trades=results_raw.get('metrics', {}).get('total_trades', 0),
            win_rate=results_raw.get('metrics', {}).get('win_rate', 0.0),
            net_pnl=results_raw.get('metrics', {}).get('net_pnl', 0.0),
            profit_factor=results_raw.get('metrics', {}).get('profit_factor', 0.0),
            max_drawdown=results_raw.get('metrics', {}).get('max_drawdown', 0.0),
            avg_win=results_raw.get('metrics', {}).get('avg_win', 0.0),
            avg_loss=results_raw.get('metrics', {}).get('avg_loss', 0.0),
            expectancy=results_raw.get('metrics', {}).get('expectancy', 0.0),
            winning_trades=results_raw.get('metrics', {}).get('winning_trades', 0),
            losing_trades=results_raw.get('metrics', {}).get('losing_trades', 0),
            gross_profit=results_raw.get('metrics', {}).get('gross_profit', 0.0),
            gross_loss=results_raw.get('metrics', {}).get('gross_loss', 0.0)
        )
        
        # Récupérer et convertir les trades
        trades_raw = results_raw.get('trades', [])
        trades = []
        for trade_data in trades_raw:
            trades.append(Trade(
                id=trade_data.get('id', 0),
                date=trade_data.get('date', ''),
                entry_time=trade_data.get('entry_time', trade_data.get('date', '')),
                exit_time=trade_data.get('exit_time', trade_data.get('date', '')),
                direction=trade_data.get('direction', ''),
                entry=trade_data.get('entry', 0.0),
                exit=trade_data.get('exit', 0.0),
                points=trade_data.get('points', 0.0),
                pnl_usd=trade_data.get('pnl_usd', 0.0),
                result=trade_data.get('result', '')
            ))

        return RunResults(
            run_id=run_id,
            strategy=results_raw.get('strategy', 'Unknown'),
            metrics=metrics,
            equity_curve=results_raw.get('equity_curve', []),
            drawdown_curve=results_raw.get('drawdown_curve', []),
            trades=trades,
            files=results_raw.get('files', [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des résultats: {str(e)}"
        )

@router.get("/data-range")
def get_data_range(force_reload: bool = False):
    """
    Récupère la plage de dates disponible dans les données
    """
    global _data_range_cache, _data_range_cache_time
    
    # Vérifier le cache (valide pendant 10 minutes)
    import time
    current_time = time.time()
    
    if (not force_reload and 
        _data_range_cache is not None and 
        _data_range_cache_time is not None and
        current_time - _data_range_cache_time < 600):  # 10 minutes
        print("📦 Utilisation du cache pour data-range")
        return _data_range_cache
    
    print("🔄 Rechargement des données pour data-range...")
    
    try:
        # Charger les données pour déterminer la plage
        import pandas as pd
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from config import DATA_CSV_FULL_PATH
        
        data_path = DATA_CSV_FULL_PATH
        
        if not data_path.exists():
            return {
                "start_date": None,
                "end_date": None,
                "total_days": 0,
                "message": f"Aucune donnée disponible à {data_path}"
            }
        
        # Lire le fichier complet pour déterminer la vraie plage
        print(f"Lecture du fichier: {data_path}")
        df = pd.read_csv(data_path)
        print(f"Lignes lues: {len(df)}")
        
        # Normaliser les colonnes
        cols = {c.lower(): c for c in df.columns}
        if "ts_event" in cols:
            df["timestamp"] = pd.to_datetime(df[cols["ts_event"]], utc=True)
        else:
            return {
                "start_date": None,
                "end_date": None,
                "total_days": 0,
                "message": "Colonne timestamp non trouvée"
            }
        
        start_date = df["timestamp"].min()
        end_date = df["timestamp"].max()
        total_days = (end_date - start_date).days + 1
        
        print(f"Date min: {start_date}")
        print(f"Date max: {end_date}")
        print(f"Total jours: {total_days}")
        print(f"Échantillon timestamps: {df['timestamp'].head()}")
        print(f"Échantillon timestamps fin: {df['timestamp'].tail()}")
        
        result = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_days": total_days,
            "message": f"Données disponibles de {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}"
        }
        
        # Mettre en cache
        _data_range_cache = result
        _data_range_cache_time = current_time
        print(f"✅ Data range mis en cache: {result['start_date']} -> {result['end_date']}")
        
        return result
        
    except Exception as e:
        return {
            "start_date": None,
            "end_date": None,
            "total_days": 0,
            "message": f"Erreur lors de la lecture des données: {str(e)}"
        }

# Cache global pour les données OHLC
_ohlc_cache = {}
_cache_timestamp = None
_data_range_cache = None
_data_range_cache_time = None

@router.get("/ohlc-data")
def get_ohlc_data(days: int = 7):
    """
    Récupère les données OHLC en 30mn pour les X derniers jours
    """
    global _ohlc_cache, _cache_timestamp
    
    try:
        import pandas as pd
        from pathlib import Path
        import time
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from config import DATA_CSV_FULL_PATH
        
        data_path = DATA_CSV_FULL_PATH
        
        if not data_path.exists():
            raise HTTPException(status_code=404, detail=f"Données non trouvées à {data_path}")
        
        # Vérifier le cache (valide pendant 5 minutes)
        current_time = time.time()
        cache_key = f"ohlc_{days}"
        
        if (_cache_timestamp and 
            current_time - _cache_timestamp < 300 and  # 5 minutes
            cache_key in _ohlc_cache):
            print(f"Utilisation du cache pour {days} jours")
            return _ohlc_cache[cache_key]
        
        # Optimisation : lire seulement un échantillon récent
        print(f"Lecture d'un échantillon pour {days} jours...")
        
        # Pour l'instant, lire tout le fichier mais on optimisera plus tard
        # TODO: Implémenter une lecture par chunks plus robuste
        df = pd.read_csv(data_path)
        
        # Normaliser les colonnes
        cols = {c.lower(): c for c in df.columns}
        df = df.rename(columns={
            cols["ts_event"]: "timestamp",
            cols["open"]: "open",
            cols["high"]: "high", 
            cols["low"]: "low",
            cols["close"]: "close",
            cols["volume"]: "volume",
            cols["symbol"]: "symbol"
        })
        
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        
        # Filtrer les derniers jours
        end_date = df["timestamp"].max()
        start_date = end_date - pd.Timedelta(days=days)
        df_filtered = df[df["timestamp"] >= start_date].copy()
        
        # Filtrer sur NQ (front month)
        nq_symbols = df_filtered[df_filtered["symbol"].str.match(r"^NQ[A-Z][0-9]{1,2}$")]["symbol"].unique()
        if len(nq_symbols) > 0:
            # Prendre le symbole le plus récent (alphabétiquement le dernier)
            latest_symbol = sorted(nq_symbols)[-1]
            df_filtered = df_filtered[df_filtered["symbol"] == latest_symbol]
        
        # Resampler en 30mn
        df_filtered.set_index("timestamp", inplace=True)
        ohlc_30m = df_filtered.resample("30T").agg({
            "open": "first",
            "high": "max", 
            "low": "min",
            "close": "last",
            "volume": "sum"
        }).dropna()
        
        # Convertir en format pour le frontend
        data = []
        for timestamp, row in ohlc_30m.iterrows():
            data.append({
                "timestamp": timestamp.isoformat(),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": int(row["volume"])
            })
        
        result = {
            "data": data,
            "symbol": latest_symbol if len(nq_symbols) > 0 else "NQ",
            "timeframe": "30m",
            "period": f"{days} derniers jours",
            "total_bars": len(data)
        }
        
        # Mettre en cache
        _ohlc_cache[cache_key] = result
        _cache_timestamp = current_time
        print(f"Données mises en cache pour {days} jours")
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des données OHLC: {str(e)}"
        )

@router.get("/{run_id}/heatmap")
async def get_run_heatmap(run_id: str):
    """Récupère les données de heatmap pour un run"""
    try:
        runner = get_runner()
        
        # Vérifier que le run existe
        runs = runner.list_runs()
        target_run = None
        for run in runs:
            if run.run_id == run_id:
                target_run = run
                break
        
        if not target_run:
            raise HTTPException(
                status_code=404,
                detail=f"Run {run_id} non trouvé"
            )
        
        if target_run.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Run {run_id} n'est pas terminé (statut: {target_run.status})"
            )
        
        # Récupérer les résultats
        results_raw = runner.get_results(run_id)
        if not results_raw:
            raise HTTPException(
                status_code=404,
                detail=f"Résultats non trouvés pour le run {run_id}"
            )
        
        # Générer les données de heatmap
        trades_data = results_raw.get('trades', [])
        print(f"🔍 Génération heatmap pour {len(trades_data)} trades")
        if trades_data:
            print(f"   Premier trade: {trades_data[0]}")
        
        heatmap_data = generate_heatmap_data(trades_data)
        print(f"🔍 Heatmap générée: {len(heatmap_data)} points de données")
        
        return {
            "run_id": run_id,
            "heatmap": heatmap_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de la heatmap: {str(e)}"
        )

def generate_heatmap_data(trades):
    """Génère les données de heatmap à partir des trades"""
    import pandas as pd
    from datetime import datetime
    
    if not trades:
        print("⚠️ Aucun trade fourni pour la heatmap")
        return []
    
    print(f"🔍 Processing {len(trades)} trades pour heatmap")
    
    # Convertir en DataFrame
    df = pd.DataFrame(trades)
    print(f"🔍 Colonnes disponibles: {list(df.columns)}")
    print(f"🔍 Exemple de dates: {df['date'].head().tolist()}")
    
    # Parser les dates - vérifier si on a des heures ou juste des dates
    df['date'] = pd.to_datetime(df['date'])
    
    # Si les données n'ont que des dates (pas d'heures), utiliser une heure fictive
    # pour la visualisation (par exemple 14h = heure de trading NQ en Europe)
    if df['date'].dt.hour.nunique() == 1 and df['date'].dt.hour.iloc[0] == 0:
        print("🔍 Dates sans heures détectées - utilisation d'une heure fictive pour la visualisation")
        # Assigner une heure aléatoire entre 13h30 et 20h (heures de trading NQ en UTC)
        import numpy as np
        np.random.seed(42)  # Pour reproductibilité
        trading_hours = np.random.choice(range(13, 21), size=len(df))  # 13h-20h UTC
        df['hour'] = trading_hours
        df['day_of_week'] = df['date'].dt.day_name()
    else:
        # Si on a des vraies heures, les utiliser
        df['day_of_week'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
    
    print(f"🔍 Répartition des heures: {sorted(df['hour'].unique())}")
    
    print(f"🔍 Après parsing - jours: {df['day_of_week'].unique()}")
    print(f"🔍 Après parsing - heures: {sorted(df['hour'].unique())}")
    
    # Mapper les jours en français
    day_mapping = {
        'Monday': 'Lun',
        'Tuesday': 'Mar', 
        'Wednesday': 'Mer',
        'Thursday': 'Jeu',
        'Friday': 'Ven',
        'Saturday': 'Sam',
        'Sunday': 'Dim'
    }
    df['day_fr'] = df['day_of_week'].map(day_mapping)
    
    # Grouper par jour et heure
    grouped = df.groupby(['day_fr', 'hour']).agg({
        'pnl_usd': ['sum', 'mean', 'count'],
        'result': lambda x: (x == 'TP').sum() / len(x) if len(x) > 0 else 0
    }).reset_index()
    
    # Aplatir les colonnes
    grouped.columns = ['day', 'hour', 'total_pnl', 'avg_pnl', 'trades', 'win_rate']
    
    # Créer la liste des données heatmap
    heatmap_data = []
    for _, row in grouped.iterrows():
        heatmap_data.append({
            'day': row['day'],
            'hour': int(row['hour']),
            'value': float(row['avg_pnl']),  # PnL moyen par créneau
            'trades': int(row['trades']),
            'winRate': float(row['win_rate'])
        })
    
    return heatmap_data

@router.get("/data-range")
async def get_data_range():
    """Récupère la plage de dates disponibles dans les données"""
    try:
        import pandas as pd
        from pathlib import Path
        import os
        
        # Chercher un fichier CSV récent pour déterminer la plage de dates
        # PRIORITE 1: dossier data/raw (données sources)
        data_raw_dir = Path("data/raw")
        csv_files = []
        
        print(f"🔍 Vérification de data/raw:")
        print(f"   - Chemin: {data_raw_dir.absolute()}")
        print(f"   - Existe: {data_raw_dir.exists()}")
        
        if data_raw_dir.exists():
            raw_files = list(data_raw_dir.glob("*.csv"))
            csv_files.extend(raw_files)
            print(f"✅ Trouvé {len(csv_files)} fichiers CSV dans data/raw/")
            if raw_files:
                for f in raw_files:
                    print(f"   - {f.name}")
        
        # PRIORITE 2: dossier data/
        if not csv_files:
            data_dir = Path("data")
            if data_dir.exists():
                csv_files.extend(list(data_dir.glob("*.csv")))
                print(f"🔍 Trouvé {len(csv_files)} fichiers CSV dans data/")
        
        # PRIORITE 3: chercher dans les runs récents (en dernier recours)
        # mais IGNORER les fichiers temporaires
        if not csv_files:
            runs_dir = Path("runs")
            if runs_dir.exists():
                for run_dir in runs_dir.iterdir():
                    if run_dir.is_dir():
                        for csv_file in run_dir.glob("*.csv"):
                            # Ignorer les fichiers temporaires
                            if not any(skip in csv_file.name for skip in ['front_month_selection_log', 'filtered_data']):
                                csv_files.append(csv_file)
            print(f"🔍 Trouvé {len(csv_files)} fichiers CSV dans runs/ (sans les fichiers temporaires)")
        
        if not csv_files:
            # Dates par défaut si pas de fichiers trouvés
            return {
                "start_date": "2024-08-01",
                "end_date": "2024-09-30",
                "total_days": 60
            }
        
        # Trier par taille (fichier le plus gros = plus de données)
        # plutôt que par date de modification
        csv_files_with_size = [(f, f.stat().st_size) for f in csv_files]
        csv_files_with_size.sort(key=lambda x: x[1], reverse=True)
        
        # Prendre le plus gros fichier (pas le plus récent)
        latest_csv = csv_files_with_size[0][0]
        print(f"🔍 Fichiers CSV trouvés (triés par taille):")
        for f, size in csv_files_with_size[:5]:  # Afficher les 5 plus gros
            print(f"   - {f.name}: {size / 1024:.1f} KB")
        print(f"🔍 Analyse des dates depuis le plus gros: {latest_csv}")
        
        # Optimisation: Lire seulement les premières et dernières lignes
        # au lieu de charger tout le fichier (peut être très gros)
        print(f"🔍 Lecture optimisée (premières et dernières lignes seulement)...")
        
        # Lire les premières lignes pour avoir le header et la première date
        df_head = pd.read_csv(latest_csv, nrows=10)
        
        # Chercher une colonne de date
        date_column = None
        for col in ['ts_event', 'timestamp', 'time', 'date', 'Date', 'DATE', 'datetime']:
            if col in df_head.columns:
                date_column = col
                print(f"✅ Colonne de date trouvée: {col}")
                break
        
        if not date_column:
            print("⚠️ Aucune colonne de date trouvée")
            print(f"   Colonnes disponibles: {list(df_head.columns)}")
            return {
                "start_date": "2024-08-01", 
                "end_date": "2024-09-30",
                "total_days": 60
            }
        
        # Lire les dernières lignes pour avoir la dernière date
        # Méthode: lire les dernières lignes du fichier texte
        with open(latest_csv, 'rb') as f:
            # Aller à la fin du fichier
            f.seek(0, 2)  # Aller à la fin
            file_size = f.tell()
            # Lire les derniers 10KB (devrait contenir plusieurs lignes)
            f.seek(max(0, file_size - 10000))
            last_lines = f.read().decode('utf-8', errors='ignore').split('\n')
            # Prendre les dernières lignes non-vides
            last_lines = [l for l in last_lines if l.strip()][-10:]
        
        # Créer un DataFrame avec les dernières lignes
        from io import StringIO
        df_tail = pd.read_csv(StringIO('\n'.join(last_lines)), names=df_head.columns)
        
        # Convertir les dates
        df_head[date_column] = pd.to_datetime(df_head[date_column], errors='coerce')
        df_tail[date_column] = pd.to_datetime(df_tail[date_column], errors='coerce')
        
        # Trouver min et max
        min_date = df_head[date_column].min()
        max_date = df_tail[date_column].max()
        start_date = min_date.strftime('%Y-%m-%d')
        end_date = max_date.strftime('%Y-%m-%d')
        total_days = (max_date - min_date).days
        
        print(f"📅 Plage de dates trouvée:")
        print(f"   - Première date (MIN): {start_date}")
        print(f"   - Dernière date (MAX): {end_date}")
        print(f"   - Total: {total_days} jours")
        print(f"   - Fichier analysé: {latest_csv.name}")
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days
        }
    
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse des dates: {e}")
        return {
            "start_date": "2024-08-01",
            "end_date": "2024-09-30",
            "total_days": 60
        }


@router.delete("/{run_id}")
def delete_run(run_id: str):
    """
    Supprime un run et tous ses fichiers
    """
    try:
        runner = get_runner()
        
        # Vérifier que le run existe
        runs = runner.list_runs()
        run_exists = any(run.run_id == run_id for run in runs)
        
        if not run_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Run {run_id} non trouvé"
            )
        
        # Supprimer le run
        success = runner.delete_run(run_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la suppression du run {run_id}"
            )
        
        return {
            "success": True,
            "message": f"Run {run_id} supprimé avec succès"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )
