#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper d'exécution des backtests existants.
Interface unifiée et non-intrusive pour lancer les stratégies.
"""

import os
import sys
import json
import uuid
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class RunConfig:
    """Configuration d'une exécution de backtest"""
    run_id: str
    strategy_name: str
    script_path: str
    base_path: str
    csv_path: Optional[str] = None
    parameters: Dict[str, Any] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.parameters is None:
            self.parameters = {}

@dataclass 
class RunStatus:
    """Statut d'une exécution"""
    run_id: str
    status: str  # 'running', 'completed', 'failed', 'pending'
    progress: float  # 0.0 à 1.0
    message: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output_files: List[str] = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []

class BacktestRunner:
    """Gestionnaire d'exécution des backtests"""
    
    def __init__(self, base_path: str, runs_dir: str = None):
        self.base_path = Path(base_path)
        self.runs_dir = Path(runs_dir) if runs_dir else self.base_path / "integration_poc" / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        
    def start_backtest(self, strategy_name: str, script_path: str, 
                      csv_path: str = None, parameters: Dict[str, Any] = None) -> str:
        """Lance un backtest en arrière-plan"""
        
        run_id = str(uuid.uuid4())[:8]
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(exist_ok=True)
        
        # Configuration de l'exécution
        config = RunConfig(
            run_id=run_id,
            strategy_name=strategy_name,
            script_path=script_path,
            base_path=str(self.base_path),
            csv_path=csv_path,
            parameters=parameters or {}
        )
        
        # Sauvegarde de la configuration
        config_file = run_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(asdict(config), f, indent=2)
        
        # Statut initial
        status = RunStatus(
            run_id=run_id,
            status='pending',
            progress=0.0,
            message='Préparation du backtest...'
        )
        self._save_status(run_id, status)
        
        # Lancement asynchrone
        self._execute_async(config)
        
        return run_id
    
    def get_status(self, run_id: str) -> Optional[RunStatus]:
        """Récupère le statut d'une exécution"""
        status_file = self.runs_dir / run_id / "status.json"
        
        if not status_file.exists():
            return None
            
        try:
            with open(status_file, 'r') as f:
                data = json.load(f)
            return RunStatus(**data)
        except Exception as e:
            return RunStatus(
                run_id=run_id,
                status='failed',
                progress=0.0,
                message='Erreur lecture statut',
                error=str(e)
            )
    
    def get_results(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les résultats d'une exécution"""
        run_dir = self.runs_dir / run_id
        results_file = run_dir / "results.json"
        
        if not results_file.exists():
            return None
            
        try:
            with open(results_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Erreur lecture résultats: {e}"}
    
    def list_runs(self) -> List[RunStatus]:
        """Liste toutes les exécutions"""
        runs = []
        
        for run_dir in self.runs_dir.iterdir():
            if run_dir.is_dir():
                status = self.get_status(run_dir.name)
                if status:
                    runs.append(status)
        
        return sorted(runs, key=lambda r: r.started_at or r.run_id, reverse=True)
    
    def _execute_async(self, config: RunConfig):
        """Exécute le backtest de manière asynchrone"""
        import threading
        
        def run_backtest():
            self._execute_backtest(config)
        
        thread = threading.Thread(target=run_backtest, daemon=True)
        thread.start()
    
    def _execute_backtest(self, config: RunConfig):
        """Exécute le backtest (méthode interne)"""
        run_id = config.run_id
        run_dir = self.runs_dir / run_id
        
        try:
            # Mise à jour du statut
            status = RunStatus(
                run_id=run_id,
                status='running',
                progress=0.1,
                message='Démarrage du backtest...',
                started_at=datetime.now().isoformat()
            )
            self._save_status(run_id, status)
            
            # Préparation des chemins
            script_path = Path(config.script_path)
            csv_path = config.csv_path or self._find_latest_csv()
            
            if not csv_path or not Path(csv_path).exists():
                raise FileNotFoundError(f"Fichier CSV introuvable: {csv_path}")
            
            # Utilisation de l'outil existant run_backtest.py
            tools_runner = self.base_path / "tools" / "run_backtest.py"
            
            if tools_runner.exists():
                # Utiliser l'outil existant
                cmd = [
                    sys.executable, str(tools_runner),
                    "--base", str(self.base_path),
                    "--script-path", str(script_path),
                    "--csv", str(csv_path)
                ]
            else:
                # Exécution directe du script
                # D'abord, patcher le CSV_PATH si nécessaire
                self._patch_csv_path(script_path, csv_path)
                cmd = [sys.executable, str(script_path)]
            
            # Mise à jour du statut
            status.progress = 0.3
            status.message = 'Exécution du backtest...'
            self._save_status(run_id, status)
            
            # Exécution avec capture des logs
            log_file = run_dir / "execution.log"
            
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=str(self.base_path),
                    text=True
                )
                
                # Attendre la fin
                return_code = process.wait()
            
            # Mise à jour du statut
            status.progress = 0.8
            status.message = 'Collecte des résultats...'
            self._save_status(run_id, status)
            
            # Collecte des résultats
            if return_code == 0:
                results = self._collect_results(config, run_dir)
                self._save_results(run_id, results)
                
                status.status = 'completed'
                status.progress = 1.0
                status.message = 'Backtest terminé avec succès'
                status.completed_at = datetime.now().isoformat()
                status.output_files = results.get('files', [])
            else:
                # Lire les logs d'erreur
                error_msg = "Erreur d'exécution"
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        error_msg = f.read()[-1000:]  # Dernières 1000 chars
                
                status.status = 'failed'
                status.progress = 0.0
                status.message = 'Échec du backtest'
                status.completed_at = datetime.now().isoformat()
                status.error = error_msg
            
        except Exception as e:
            status.status = 'failed'
            status.progress = 0.0
            status.message = f'Erreur: {str(e)}'
            status.completed_at = datetime.now().isoformat()
            status.error = str(e)
        
        finally:
            self._save_status(run_id, status)
    
    def _find_latest_csv(self) -> Optional[str]:
        """Trouve le fichier CSV le plus récent"""
        data_dir = self.base_path / "data" / "raw"
        
        if not data_dir.exists():
            return None
        
        csv_files = list(data_dir.glob("*.csv"))
        if not csv_files:
            return None
        
        # Retourner le plus récent
        latest = max(csv_files, key=lambda p: p.stat().st_mtime)
        return str(latest)
    
    def _patch_csv_path(self, script_path: Path, csv_path: str):
        """Patch le CSV_PATH dans le script (comme l'outil existant)"""
        import re
        
        content = script_path.read_text(encoding='utf-8')
        
        new_content, n = re.subn(
            r'CSV_PATH\s*=\s*[ru]?["\'].*?["\']',
            f'CSV_PATH = r"{Path(csv_path).as_posix()}"',
            content,
            flags=re.DOTALL
        )
        
        if n > 0:
            # Créer une copie temporaire
            backup_path = script_path.with_suffix('.py.backup')
            shutil.copy2(script_path, backup_path)
            
            # Écrire le contenu modifié
            script_path.write_text(new_content, encoding='utf-8')\n    \n    def _collect_results(self, config: RunConfig, run_dir: Path) -> Dict[str, Any]:\n        \"\"\"Collecte les résultats du backtest\"\"\"\n        results = {\n            'strategy': config.strategy_name,\n            'files': [],\n            'metrics': {},\n            'trades_count': 0,\n            'error': None\n        }\n        \n        try:\n            # Chercher les fichiers de sortie dans différents endroits\n            search_paths = [\n                self.base_path,  # Racine\n                self.base_path / \"data\" / \"outputs\",  # Outputs\n                self.base_path / \"backtests\"  # Backtests\n            ]\n            \n            output_files = []\n            \n            for search_path in search_paths:\n                if search_path.exists():\n                    # Chercher les CSV récents (dernières 5 minutes)\n                    recent_time = datetime.now().timestamp() - 300\n                    \n                    for csv_file in search_path.glob(\"*.csv\"):\n                        if csv_file.stat().st_mtime > recent_time:\n                            # Copier vers le dossier de run\n                            dest_file = run_dir / csv_file.name\n                            shutil.copy2(csv_file, dest_file)\n                            output_files.append(csv_file.name)\n            \n            results['files'] = output_files\n            \n            # Analyser le fichier de trades principal si trouvé\n            trades_file = None\n            for filename in output_files:\n                if 'trades' in filename.lower():\n                    trades_file = run_dir / filename\n                    break\n            \n            if trades_file and trades_file.exists():\n                results.update(self._analyze_trades_file(trades_file))\n            \n        except Exception as e:\n            results['error'] = str(e)\n        \n        return results\n    \n    def _analyze_trades_file(self, trades_file: Path) -> Dict[str, Any]:\n        \"\"\"Analyse un fichier de trades pour extraire les métriques\"\"\"\n        try:\n            import pandas as pd\n            \n            df = pd.read_csv(trades_file)\n            \n            if df.empty:\n                return {'trades_count': 0, 'metrics': {}}\n            \n            # Filtrer les trades réels (avec PnL)\n            real_trades = df[df['result'].isin(['TP', 'SL', 'EOD'])].copy()\n            \n            if real_trades.empty:\n                return {'trades_count': 0, 'metrics': {}}\n            \n            # Calcul des métriques\n            wins = real_trades[real_trades['result'] == 'TP']\n            losses = real_trades[real_trades['result'] != 'TP']\n            \n            net_pnl = real_trades['pnl_usd'].sum()\n            win_rate = len(wins) / len(real_trades) if len(real_trades) > 0 else 0\n            \n            gross_profit = wins['pnl_usd'].sum() if len(wins) > 0 else 0\n            gross_loss = -losses['pnl_usd'].sum() if len(losses) > 0 else 0\n            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')\n            \n            # Drawdown\n            equity_curve = real_trades['pnl_usd'].cumsum()\n            running_max = equity_curve.cummax()\n            drawdown = equity_curve - running_max\n            max_drawdown = drawdown.min()\n            \n            metrics = {\n                'total_trades': len(real_trades),\n                'winning_trades': len(wins),\n                'losing_trades': len(losses),\n                'win_rate': win_rate,\n                'net_pnl': net_pnl,\n                'gross_profit': gross_profit,\n                'gross_loss': gross_loss,\n                'profit_factor': profit_factor,\n                'max_drawdown': max_drawdown,\n                'avg_win': wins['pnl_usd'].mean() if len(wins) > 0 else 0,\n                'avg_loss': losses['pnl_usd'].mean() if len(losses) > 0 else 0,\n                'expectancy': net_pnl / len(real_trades) if len(real_trades) > 0 else 0\n            }\n            \n            return {\n                'trades_count': len(real_trades),\n                'metrics': metrics,\n                'equity_curve': equity_curve.tolist(),\n                'drawdown_curve': drawdown.tolist()\n            }\n            \n        except Exception as e:\n            return {'trades_count': 0, 'metrics': {}, 'error': str(e)}\n    \n    def _save_status(self, run_id: str, status: RunStatus):\n        \"\"\"Sauvegarde le statut d'une exécution\"\"\"\n        status_file = self.runs_dir / run_id / \"status.json\"\n        status_file.parent.mkdir(exist_ok=True)\n        \n        with open(status_file, 'w') as f:\n            json.dump(asdict(status), f, indent=2)\n    \n    def _save_results(self, run_id: str, results: Dict[str, Any]):\n        \"\"\"Sauvegarde les résultats d'une exécution\"\"\"\n        results_file = self.runs_dir / run_id / \"results.json\"\n        \n        with open(results_file, 'w') as f:\n            json.dump(results, f, indent=2)\n\n# Interface simple pour Streamlit\ndef create_runner(base_path: str) -> BacktestRunner:\n    \"\"\"Crée un runner pour le chemin de base donné\"\"\"\n    return BacktestRunner(base_path)\n\nif __name__ == \"__main__\":\n    # Test du runner\n    import sys\n    \n    if len(sys.argv) < 2:\n        print(\"Usage: python run_backtest.py <base_path> [strategy_script]\")\n        sys.exit(1)\n    \n    base_path = sys.argv[1]\n    runner = create_runner(base_path)\n    \n    if len(sys.argv) > 2:\n        # Lancer un backtest\n        strategy_script = sys.argv[2]\n        strategy_name = Path(strategy_script).stem\n        \n        print(f\"Lancement du backtest: {strategy_name}\")\n        run_id = runner.start_backtest(strategy_name, strategy_script)\n        print(f\"Run ID: {run_id}\")\n        \n        # Suivre le statut\n        import time\n        while True:\n            status = runner.get_status(run_id)\n            if status:\n                print(f\"Statut: {status.status} - {status.message} ({status.progress:.1%})\")\n                if status.status in ['completed', 'failed']:\n                    break\n            time.sleep(2)\n    else:\n        # Lister les runs\n        runs = runner.list_runs()\n        print(f\"\\n=== Exécutions récentes ({len(runs)}) ===\")\n        for run in runs[:10]:  # 10 plus récentes\n            print(f\"{run.run_id}: {run.status} - {run.message}\")
