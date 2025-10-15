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
from dataclasses import dataclass, asdict, field

@dataclass
class RunConfig:
    """Configuration d'une exécution de backtest"""
    run_id: str
    strategy_name: str
    script_path: str
    base_path: str
    csv_path: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    name: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass 
class RunStatus:
    """Statut d'une exécution"""
    run_id: str
    status: str  # 'running', 'completed', 'failed', 'pending'
    progress: float  # 0.0 à 1.0
    message: str
    name: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output_files: List[str] = field(default_factory=list)

class BacktestRunner:
    """Gestionnaire d'exécution des backtests"""
    
    def __init__(self, base_path: str, runs_dir: str = None):
        self.base_path = Path(base_path)
        
        # Utiliser un dossier temporaire système pour éviter que uvicorn le surveille
        if runs_dir:
            self.runs_dir = Path(runs_dir)
        else:
            # Créer le dossier runs au PARENT du backend (pas surveillé par uvicorn)
            self.runs_dir = self.base_path.parent / "backend_runs"
        
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Dossier runs: {self.runs_dir}")
        
    def start_backtest(self, strategy_name: str, script_path: str, 
                      csv_path: str = None, parameters: Dict[str, Any] = None, name: str = None) -> str:
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
            parameters=parameters if parameters is not None else {},
            name=name
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
            message='Préparation du backtest...',
            name=name
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
    
    def delete_run(self, run_id: str) -> bool:
        """Supprime une exécution et tous ses fichiers"""
        import shutil
        
        run_dir = self.runs_dir / run_id
        
        if not run_dir.exists():
            return False
        
        try:
            shutil.rmtree(run_dir)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du run {run_id}: {e}")
            return False
    
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
                name=config.name,
                started_at=datetime.now().isoformat()
            )
            self._save_status(run_id, status)
            
            # Préparation des chemins
            script_path = Path(config.script_path)
            original_csv_path = config.csv_path or self._find_latest_csv()
            
            if not original_csv_path or not Path(original_csv_path).exists():
                raise FileNotFoundError(f"Fichier CSV introuvable: {original_csv_path}")
            
            # Filtrage des données selon les paramètres de dates
            print(f"🔍 Paramètres reçus: {config.parameters}")
            csv_path = self._filter_csv_by_dates(original_csv_path, config.parameters, run_dir)
            
            # TOUJOURS utiliser l'exécution directe avec copie temporaire
            # (tools/run_backtest.py modifie l'original et cause des reloads uvicorn)
            print(f"📝 Création d'une copie temporaire du script pour éviter les reloads...")
            patched_script = self._patch_csv_path(script_path, csv_path, run_dir)
            cmd = [sys.executable, str(patched_script)]
            
            # Mise à jour du statut
            status.progress = 0.3
            status.message = 'Exécution du backtest...'
            self._save_status(run_id, status)
            
            # Exécution avec capture des logs
            log_file = run_dir / "execution.log"
            
            print(f"🚀 Lancement commande: {' '.join(cmd)}")
            print(f"📁 Workdir: {run_dir}")
            print(f"📝 Log file: {log_file}")
            
            with open(log_file, 'w') as f:
                f.write(f"=== Commande ===\n")
                f.write(f"{' '.join(cmd)}\n\n")
                f.write(f"=== Exécution ===\n")
                f.flush()
                
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=str(run_dir),  # MODIFIÉ: Exécuter dans le dossier du run
                    text=True
                )
                
                print(f"⏳ Attente de fin du processus (PID: {process.pid})...")
                # Attendre la fin
                return_code = process.wait()
                print(f"✅ Processus terminé avec code: {return_code}")
            
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
    
    def _patch_csv_path(self, script_path: Path, csv_path: str, run_dir: Path = None):
        """Patch le CSV_PATH dans le script en créant une copie temporaire"""
        import re
        
        content = script_path.read_text(encoding='utf-8')
        
        # Pattern pour matcher les deux formats:
        # 1. CSV_PATH = r"chemin" ou CSV_PATH = "chemin"
        # 2. CSV_PATH = str(DATA_CSV_FULL_PATH)
        patterns = [
            (r'CSV_PATH\s*=\s*[ru]?["\'].*?["\']', f'CSV_PATH = r"{Path(csv_path).as_posix()}"'),
            (r'CSV_PATH\s*=\s*str\(DATA_CSV_FULL_PATH\)', f'CSV_PATH = r"{Path(csv_path).as_posix()}"'),
        ]
        
        new_content = content
        total_replacements = 0
        
        for pattern, replacement in patterns:
            new_content, n = re.subn(pattern, replacement, new_content, flags=re.DOTALL)
            total_replacements += n
        
        if run_dir:
            # Créer une copie DANS le dossier du run (ne modifie PAS l'original!)
            temp_script = run_dir / script_path.name
            
            if total_replacements > 0:
                # CSV_PATH trouvé et remplacé
                print(f"✅ CSV_PATH patché ({total_replacements} occurrence(s)) dans la copie temporaire")
                
                # Supprimer les imports de config qui ne fonctionneront pas
                # Supprimer ligne par ligne pour être plus robuste
                lines = new_content.split('\n')
                filtered_lines = []
                skip_next = 0
                
                for i, line in enumerate(lines):
                    if skip_next > 0:
                        skip_next -= 1
                        continue
                    
                    # Détecter le début du bloc d'import config
                    if 'from config import DATA_CSV_FULL_PATH' in line:
                        # Remonter pour supprimer les lignes précédentes liées
                        # Supprimer jusqu'à 5 lignes avant si elles contiennent sys.path ou import sys
                        lines_to_remove = 0
                        for j in range(min(5, len(filtered_lines))):
                            idx = len(filtered_lines) - 1 - j
                            if idx >= 0:
                                prev_line = filtered_lines[idx]
                                if ('sys.path.insert' in prev_line or 
                                    'import sys' in prev_line or
                                    'from pathlib import Path' in prev_line or
                                    '# Ajouter le chemin' in prev_line):
                                    lines_to_remove += 1
                                else:
                                    break
                        
                        # Supprimer les lignes identifiées
                        for _ in range(lines_to_remove):
                            if filtered_lines:
                                filtered_lines.pop()
                        
                        continue  # Ne pas ajouter la ligne actuelle
                    
                    filtered_lines.append(line)
                
                new_content = '\n'.join(filtered_lines)
                temp_script.write_text(new_content, encoding='utf-8')
            else:
                # CSV_PATH non trouvé, copier tel quel (le script utilise peut-être un autre mécanisme)
                print(f"⚠️ CSV_PATH non trouvé dans {script_path.name}, copie du script original")
                temp_script.write_text(content, encoding='utf-8')
            
            return temp_script
        
        return script_path
    
    def _collect_results(self, config: RunConfig, run_dir: Path) -> Dict[str, Any]:
        """Collecte les résultats du backtest"""
        results = {
            'strategy': config.strategy_name,
            'files': [],
            'metrics': {},
            'trades': [],
            'trades_count': 0,
            'error': None,
            'debug_info': []
        }
        
        try:
            # PRIORITÉ 1: Chercher d'abord dans le dossier du run (fichiers générés par le script)
            # PRIORITÉ 2: Chercher dans les dossiers globaux (fallback)
            search_paths = [
                run_dir,  # NOUVEAU: Dossier du run (priorité absolue)
                self.base_path,  # Racine
                self.base_path / "data" / "outputs",  # Outputs
                self.base_path / "backtests"  # Backtests
            ]
            
            output_files = []
            debug_info = []
            
            # Temps de référence plus large (10 minutes)
            recent_time = datetime.now().timestamp() - 600
            
            for search_path in search_paths:
                if search_path.exists():
                    debug_info.append(f"Recherche dans: {search_path}")
                    
                    csv_files = list(search_path.glob("*.csv"))
                    debug_info.append(f"  Trouvé {len(csv_files)} fichiers CSV")
                    
                    for csv_file in csv_files:
                        # Ignorer filtered_data.csv (c'est l'input, pas un résultat)
                        if csv_file.name == 'filtered_data.csv':
                            continue
                        
                        file_time = csv_file.stat().st_mtime
                        age_minutes = (datetime.now().timestamp() - file_time) / 60
                        
                        debug_info.append(f"  {csv_file.name}: {age_minutes:.1f}min")
                        
                        if file_time > recent_time:
                            # Si le fichier est déjà dans run_dir, pas besoin de copier
                            if csv_file.parent == run_dir:
                                output_files.append(csv_file.name)
                                debug_info.append(f"    -> Déjà dans run_dir")
                            else:
                                # Copier vers le dossier de run
                                dest_file = run_dir / csv_file.name
                                shutil.copy2(csv_file, dest_file)
                                output_files.append(csv_file.name)
                                debug_info.append(f"    -> Copié")
                else:
                    debug_info.append(f"Chemin inexistant: {search_path}")
            
            results['files'] = output_files
            results['debug_info'] = debug_info
            
            # Si aucun fichier récent, essayer de prendre le plus récent
            if not output_files:
                debug_info.append("Aucun fichier récent, recherche du plus récent...")
                all_csv_files = []
                
                for search_path in search_paths:
                    if search_path.exists():
                        all_csv_files.extend(search_path.glob("*.csv"))
                
                if all_csv_files:
                    # Prendre le plus récent
                    latest_file = max(all_csv_files, key=lambda p: p.stat().st_mtime)
                    
                    # Si le fichier est déjà dans run_dir, pas besoin de copier
                    if latest_file.parent == run_dir:
                        output_files.append(latest_file.name)
                        debug_info.append(f"Fichier le plus récent (déjà dans run_dir): {latest_file.name}")
                    else:
                        dest_file = run_dir / latest_file.name
                        shutil.copy2(latest_file, dest_file)
                        output_files.append(latest_file.name)
                        debug_info.append(f"Fichier le plus récent (copié): {latest_file.name}")
                    
                    results['files'] = output_files
            
            # Analyser le fichier de trades principal si trouvé
            trades_file = None
            for filename in output_files:
                if 'trades' in filename.lower() or 'opr_trades' in filename.lower():
                    trades_file = run_dir / filename
                    debug_info.append(f"Fichier de trades trouvé: {filename}")
                    break
            
            if trades_file and trades_file.exists():
                trade_results = self._analyze_trades_file(trades_file)
                results.update(trade_results)
                debug_info.append(f"Analyse trades: {trade_results.get('trades_count', 0)} trades")
            else:
                debug_info.append("Aucun fichier de trades trouvé")
                # Créer des métriques par défaut
                results['metrics'] = {
                    'total_trades': 0,
                    'win_rate': 0.0,
                    'net_pnl': 0.0,
                    'profit_factor': 0.0,
                    'max_drawdown': 0.0
                }
                results['trades'] = []
            
        except Exception as e:
            results['error'] = str(e)
            results['debug_info'].append(f"Erreur: {e}")
        
        return results
    
    def _analyze_trades_file(self, trades_file: Path) -> Dict[str, Any]:
        """Analyse un fichier de trades pour extraire les métriques"""
        try:
            import pandas as pd
            
            df = pd.read_csv(trades_file)
            
            if df.empty:
                return {'trades_count': 0, 'metrics': {}, 'trades': []}
            
            # Filtrer les trades réels (avec PnL)
            real_trades = df[df['result'].isin(['TP', 'SL', 'EOD'])].copy()
            
            if real_trades.empty:
                return {'trades_count': 0, 'metrics': {}, 'trades': []}
            
            # Calcul des métriques
            wins = real_trades[real_trades['result'] == 'TP']
            losses = real_trades[real_trades['result'] != 'TP']
            
            net_pnl = float(real_trades['pnl_usd'].sum())
            win_rate = len(wins) / len(real_trades) if len(real_trades) > 0 else 0.0
            
            gross_profit = float(wins['pnl_usd'].sum()) if len(wins) > 0 else 0.0
            gross_loss = float(-losses['pnl_usd'].sum()) if len(losses) > 0 else 0.0
            
            # Gérer le profit factor pour éviter les valeurs infinies
            if gross_loss > 0:
                profit_factor = gross_profit / gross_loss
            elif gross_profit > 0:
                profit_factor = 999.99  # Très grand nombre au lieu d'infini
            else:
                profit_factor = 0.0
            
            # Drawdown
            equity_curve = real_trades['pnl_usd'].cumsum()
            running_max = equity_curve.cummax()
            drawdown = equity_curve - running_max
            max_drawdown = float(drawdown.min())
            
            # Sécuriser toutes les valeurs pour éviter NaN/inf
            avg_win = float(wins['pnl_usd'].mean()) if len(wins) > 0 else 0.0
            avg_loss = float(losses['pnl_usd'].mean()) if len(losses) > 0 else 0.0
            expectancy = net_pnl / len(real_trades) if len(real_trades) > 0 else 0.0
            
            # Remplacer NaN par 0
            import math
            if math.isnan(avg_win): avg_win = 0.0
            if math.isnan(avg_loss): avg_loss = 0.0
            if math.isnan(expectancy): expectancy = 0.0
            if math.isnan(max_drawdown): max_drawdown = 0.0
            if math.isinf(profit_factor): profit_factor = 999.99
            
            metrics = {
                'total_trades': len(real_trades),
                'winning_trades': len(wins),
                'losing_trades': len(losses),
                'win_rate': float(win_rate),
                'net_pnl': net_pnl,
                'gross_profit': gross_profit,
                'gross_loss': gross_loss,
                'profit_factor': float(profit_factor),
                'max_drawdown': max_drawdown,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'expectancy': expectancy
            }
            
            # Préparer la liste des trades pour le frontend
            trades_list = []
            
            # Debug: voir les colonnes disponibles
            print(f"🔍 Colonnes du DataFrame: {list(real_trades.columns)}")
            if len(real_trades) > 0:
                print(f"🔍 Premier trade (colonnes): {dict(real_trades.iloc[0])}")
            
            for idx, (_, trade) in enumerate(real_trades.iterrows()):
                # Mapping des colonnes selon le CSV réel
                entry_time = trade.get('entry_time', trade.get('date', 'N/A'))
                exit_time = trade.get('exit_time', trade.get('date', 'N/A'))
                
                # Debug pour le premier trade
                if idx == 0:
                    print(f"🔍 Premier trade - entry_time: {entry_time}")
                    print(f"🔍 Premier trade - exit_time: {exit_time}")
                    print(f"🔍 Premier trade - date: {trade.get('date', 'N/A')}")
                
                # Formater la date pour l'affichage (garder seulement la date)
                if pd.notna(entry_time) and str(entry_time) != 'N/A' and str(entry_time) != '':
                    try:
                        date_str = str(entry_time).split(' ')[0]  # Garder seulement la date
                        entry_time_str = str(entry_time)  # Garder l'heure complète
                    except:
                        date_str = str(entry_time)
                        entry_time_str = str(entry_time)
                else:
                    date_str = str(trade.get('date', 'N/A'))
                    entry_time_str = str(trade.get('date', 'N/A'))
                
                # Formater exit_time
                if pd.notna(exit_time) and str(exit_time) != 'N/A' and str(exit_time) != '':
                    exit_time_str = str(exit_time)
                else:
                    exit_time_str = str(trade.get('date', 'N/A'))
                
                # Récupérer les valeurs directement
                def safe_float(val, default=0.0):
                    try:
                        if pd.isna(val) or val == '' or val is None:
                            return default
                        result = float(val)
                        if math.isnan(result) or math.isinf(result):
                            return default
                        return result
                    except:
                        return default
                
                entry_val = safe_float(trade.get('entry', 0))
                exit_val = safe_float(trade.get('exit', 0))
                points_val = safe_float(trade.get('points', 0))
                pnl_val = safe_float(trade.get('pnl_usd', 0))
                
                trades_list.append({
                    'id': idx + 1,
                    'date': date_str,
                    'entry_time': entry_time_str,
                    'exit_time': exit_time_str,
                    'direction': str(trade.get('direction', 'UNKNOWN')).upper(),
                    'entry': entry_val,
                    'exit': exit_val,
                    'points': points_val,
                    'pnl_usd': pnl_val,
                    'result': trade.get('result', 'UNKNOWN')
                })

            return {
                'trades_count': len(real_trades),
                'metrics': metrics,
                'trades': trades_list,
                'equity_curve': equity_curve.tolist(),
                'drawdown_curve': drawdown.tolist()
            }
            
        except Exception as e:
            return {'trades_count': 0, 'metrics': {}, 'trades': [], 'error': str(e)}
    
    def _save_status(self, run_id: str, status: RunStatus):
        """Sauvegarde le statut d'une exécution"""
        status_file = self.runs_dir / run_id / "status.json"
        status_file.parent.mkdir(exist_ok=True)
        
        with open(status_file, 'w') as f:
            json.dump(asdict(status), f, indent=2)
    
    def _save_results(self, run_id: str, results: Dict[str, Any]):
        """Sauvegarde les résultats d'une exécution"""
        results_file = self.runs_dir / run_id / "results.json"
        
        try:
            # Nettoyer les résultats pour la sérialisation JSON
            clean_results = self._clean_for_json(results)
            
            with open(results_file, 'w') as f:
                json.dump(clean_results, f, indent=2)
                
            # Vérifier que le fichier a été créé
            if results_file.exists():
                size = results_file.stat().st_size
                print(f"✅ Résultats sauvegardés: {results_file} ({size} bytes)")
            else:
                print(f"❌ Échec sauvegarde: {results_file}")
                
        except Exception as e:
            print(f"❌ Erreur sauvegarde résultats: {e}")
            # Sauvegarder au moins les infos de base
            fallback_results = {
                'strategy': results.get('strategy', 'Unknown'),
                'error': f'Erreur sérialisation: {str(e)}',
                'debug_info': results.get('debug_info', []),
                'files': results.get('files', []),
                'trades_count': results.get('trades_count', 0)
            }
            
            with open(results_file, 'w') as f:
                json.dump(fallback_results, f, indent=2)
    
    def _filter_csv_by_dates(self, csv_path: str, parameters: Dict[str, Any], run_dir: Path) -> str:
        """Filtre le CSV selon les paramètres de dates START_DATE et END_DATE"""
        import pandas as pd
        from datetime import datetime
        
        start_date = parameters.get('START_DATE')
        end_date = parameters.get('END_DATE')
        
        # Si pas de dates spécifiées, retourner le fichier original
        if not start_date or not end_date or start_date == '' or end_date == '':
            print(f"🔄 Aucun filtrage de dates - utilisation du CSV complet")
            return csv_path
        
        try:
            print(f"🔄 Filtrage CSV par dates: {start_date} à {end_date}")
            
            # Charger le CSV
            df = pd.read_csv(csv_path)
            print(f"📁 CSV chargé: {len(df)} lignes, colonnes: {list(df.columns)}")
            
            # Identifier la colonne de date (essayer plusieurs noms possibles)
            date_columns = ['ts_event', 'Date', 'date', 'DateTime', 'datetime', 'timestamp', 'Timestamp']
            date_col = None
            
            for col in date_columns:
                if col in df.columns:
                    date_col = col
                    break
            
            if not date_col:
                print(f"⚠️ Aucune colonne de date trouvée dans {list(df.columns)}")
                return csv_path
            
            print(f"📅 Colonne de date détectée: '{date_col}'")
            
            # Convertir la colonne de date
            df[date_col] = pd.to_datetime(df[date_col])
            
            # Afficher la plage de dates disponibles
            min_date = df[date_col].min()
            max_date = df[date_col].max()
            print(f"📊 Plage de dates dans le CSV: {min_date.date()} à {max_date.date()}")
            
            # Convertir les dates de filtrage avec timezone UTC pour correspondre au CSV
            start_dt = pd.to_datetime(start_date).tz_localize('UTC')
            end_dt = pd.to_datetime(end_date).tz_localize('UTC')
            
            # Ajouter 1 jour à end_dt pour inclure toute la journée de fin
            end_dt = end_dt + pd.Timedelta(days=1)
            print(f"🎯 Filtrage demandé: {start_dt.date()} à {end_dt.date()}")
            
            # Vérifier si les dates de filtrage sont dans la plage disponible
            if start_dt > max_date or end_dt < min_date:
                print(f"⚠️ Les dates de filtrage sont en dehors de la plage disponible!")
                print(f"   Demandé: {start_dt.date()} à {end_dt.date()}")
                print(f"   Disponible: {min_date.date()} à {max_date.date()}")
            
            # Filtrer les données
            mask = (df[date_col] >= start_dt) & (df[date_col] <= end_dt)
            filtered_df = df[mask]
            
            print(f"📊 Données filtrées: {len(filtered_df)} lignes sur {len(df)} ({len(filtered_df)/len(df)*100:.1f}%)")
            
            if len(filtered_df) == 0:
                print(f"❌ Aucune donnée dans la période demandée! Utilisation du CSV complet.")
                return csv_path
            
            # Sauvegarder le CSV filtré
            filtered_csv_path = run_dir / "filtered_data.csv"
            filtered_df.to_csv(filtered_csv_path, index=False)
            
            return str(filtered_csv_path)
            
        except Exception as e:
            print(f"❌ Erreur lors du filtrage CSV: {e}")
            print(f"🔄 Utilisation du CSV original")
            return csv_path

    def _clean_for_json(self, obj):
        """Nettoie un objet pour la sérialisation JSON"""
        if isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_for_json(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        elif hasattr(obj, 'isoformat'):  # datetime
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        else:
            # Convertir en string pour les objets non-sérialisables
            return str(obj)

# Interface simple pour Streamlit
def create_runner(base_path: str) -> BacktestRunner:
    """Crée un runner pour le chemin de base donné"""
    return BacktestRunner(base_path)
