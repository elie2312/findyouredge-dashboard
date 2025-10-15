"""
Router pour les stratégies Ninja Trader
Lit les fichiers CSV du dossier ninja_runs
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime

router = APIRouter()

# Chemin vers le dossier ninja_runs
BACKEND_PATH = Path(__file__).parent.parent
NINJA_RUNS_PATH = BACKEND_PATH.parent / "ninja_runs"


def clean_for_json(obj):
    """Nettoie récursivement un objet pour la sérialisation JSON"""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return clean_for_json(obj.tolist())
    elif pd.isna(obj):
        return None
    elif isinstance(obj, (int, float, str, bool, type(None))):
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return None
        return obj
    else:
        return str(obj)


def calculate_strategy_stats(df: pd.DataFrame, filename: str = "") -> Dict[str, Any]:
    """Calcule les statistiques de base d'une stratégie"""
    
    print(f"\n🔍 Analyse de {filename}")
    print(f"   Colonnes disponibles: {list(df.columns)}")
    print(f"   Nombre de lignes: {len(df)}")
    
    # Détection des colonnes pertinentes (flexible)
    pnl_col = None
    
    # Essayer différentes variantes de noms de colonnes
    possible_pnl_names = ['profit', 'pnl', 'bénéfice', 'p&l', 'pl', 'net', 'gain', 'loss', 'result']
    
    for col in df.columns:
        col_lower = col.lower().strip()
        for pnl_name in possible_pnl_names:
            if pnl_name in col_lower:
                pnl_col = col
                print(f"   ✅ Colonne PnL trouvée: '{col}'")
                break
        if pnl_col:
            break
    
    if pnl_col is None:
        # Essayer de trouver une colonne numérique qui pourrait être le PnL
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        print(f"   Colonnes numériques: {numeric_cols}")
        if len(numeric_cols) > 0:
            # Prendre la dernière colonne numérique (souvent le PnL)
            pnl_col = numeric_cols[-1]
            print(f"   ⚠️ Utilisation de la colonne numérique: '{pnl_col}'")
    
    total_trades = len(df)
    
    if pnl_col and pnl_col in df.columns:
        print(f"   Échantillon de valeurs brutes: {df[pnl_col].head().tolist()}")
        
        # Nettoyer les valeurs : enlever $, €, espaces, remplacer virgule par point
        def clean_pnl_value(val):
            if pd.isna(val):
                return None
            val_str = str(val).strip()
            # Enlever les symboles monétaires et espaces
            val_str = val_str.replace('$', '').replace('€', '').replace(' ', '').replace(';', '')
            # Remplacer virgule par point pour les décimales
            val_str = val_str.replace(',', '.')
            try:
                return float(val_str)
            except:
                return None
        
        pnl_values = df[pnl_col].apply(clean_pnl_value).dropna()
        print(f"   Échantillon de valeurs nettoyées: {pnl_values.head().tolist()}")
        print(f"   Valeurs PnL après conversion: {len(pnl_values)} valeurs valides")
        
        if len(pnl_values) > 0:
            total_pnl = float(pnl_values.sum())
            winning_trades = len(pnl_values[pnl_values > 0])
            losing_trades = len(pnl_values[pnl_values < 0])
            winrate = (winning_trades / len(pnl_values) * 100) if len(pnl_values) > 0 else 0
            print(f"   📊 Stats: PnL={total_pnl:.2f}, W={winning_trades}, L={losing_trades}, WR={winrate:.1f}%")
        else:
            total_pnl = 0
            winning_trades = 0
            losing_trades = 0
            winrate = 0
    else:
        print(f"   ❌ Aucune colonne PnL trouvée!")
        total_pnl = 0
        winning_trades = 0
        losing_trades = 0
        winrate = 0
    
    # S'assurer que toutes les valeurs sont JSON-compatibles
    def safe_value(val):
        if val is None:
            return 0
        if isinstance(val, (int, float)):
            if np.isnan(val) or np.isinf(val):
                return 0
            return val
        return val
    
    return {
        "total_trades": int(safe_value(total_trades)),
        "total_pnl": round(float(safe_value(total_pnl)), 2),
        "winning_trades": int(safe_value(winning_trades)),
        "losing_trades": int(safe_value(losing_trades)),
        "winrate": round(float(safe_value(winrate)), 2),
        "pnl_column": pnl_col
    }


@router.get("")
def list_ninja_strategies(
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    market: Optional[str] = Query(None, description="Marché à filtrer (ex: NQ, ES, YM)")
):
    """
    Liste toutes les stratégies disponibles dans le dossier ninja_runs
    Peut filtrer par plage de dates et par marché
    """
    if not NINJA_RUNS_PATH.exists():
        return {"strategies": [], "markets": []}
    
    strategies = []
    markets_set = set()
    
    try:
        # Scanner les fichiers CSV dans le dossier principal ET les sous-dossiers
        csv_files = []
        
        # Fichiers à la racine (pour rétrocompatibilité)
        csv_files.extend([(f, None) for f in NINJA_RUNS_PATH.glob("*.csv")])
        
        # Fichiers dans les sous-dossiers (marchés)
        for market_dir in NINJA_RUNS_PATH.iterdir():
            if market_dir.is_dir():
                market_name = market_dir.name
                markets_set.add(market_name)
                for csv_file in market_dir.glob("*.csv"):
                    csv_files.append((csv_file, market_name))
        
        # Filtrer par marché si spécifié
        if market:
            csv_files = [(f, m) for f, m in csv_files if m == market]
        
        for csv_file, market_name in csv_files:
            try:
                # Lire le CSV avec détection automatique du séparateur
                df = pd.read_csv(csv_file, sep=None, engine='python')
                
                # Filtrer par date si les paramètres sont fournis
                if start_date or end_date:
                    print(f"\n📅 Filtrage demandé pour {csv_file.name}: {start_date} -> {end_date}")
                    print(f"   Colonnes disponibles: {list(df.columns)}")
                    
                    # Chercher la colonne de date (plusieurs noms possibles, en priorité "Heure")
                    date_columns = [col for col in df.columns if 'heure' in col.lower() and 'sortie' in col.lower()]
                    
                    # Si pas trouvé, chercher d'autres colonnes de date
                    if not date_columns:
                        date_columns = [col for col in df.columns if any(x in col.lower() for x in ['date', 'heure', 'time'])]
                    
                    print(f"   Colonnes de date trouvées: {date_columns}")
                    
                    if date_columns:
                        # Utiliser la première colonne de date trouvée (généralement "Heure de sortie")
                        date_col = date_columns[0]
                        print(f"   Utilisation de la colonne: {date_col}")
                        
                        try:
                            # Convertir en datetime avec format français (DD/MM/YYYY)
                            df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y %H:%M:%S', errors='coerce')
                            
                            # Si ça n'a pas marché, essayer d'autres formats
                            if df[date_col].isna().all():
                                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                            
                            print(f"   Lignes avant filtrage: {len(df)}")
                            print(f"   Plage de dates dans les données: {df[date_col].min()} -> {df[date_col].max()}")
                            
                            # Filtrer par date de début
                            if start_date:
                                start_dt = pd.to_datetime(start_date)
                                print(f"   Filtre début: {start_dt}")
                                df = df[df[date_col] >= start_dt]
                                print(f"   Lignes après filtre début: {len(df)}")
                            
                            # Filtrer par date de fin
                            if end_date:
                                end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)  # Inclure toute la journée
                                print(f"   Filtre fin: {end_dt}")
                                df = df[df[date_col] < end_dt]
                                print(f"   Lignes après filtre fin: {len(df)}")
                        except Exception as e:
                            print(f"   ❌ Erreur lors du filtrage de date: {e}")
                    else:
                        print(f"   ⚠️ Aucune colonne de date trouvée!")
                
                # Calculer les stats sur les données filtrées
                stats = calculate_strategy_stats(df, csv_file.name)
                
                # Créer un ID unique qui inclut le marché si présent
                strategy_id = f"{market_name}/{csv_file.stem}" if market_name else csv_file.stem
                
                strategies.append({
                    "id": strategy_id,
                    "name": csv_file.stem,
                    "filename": csv_file.name,
                    "market": market_name,
                    "stats": stats
                })
            except Exception as e:
                print(f"Erreur lors de la lecture de {csv_file.name}: {e}")
                # Ajouter quand même la stratégie avec des stats vides
                strategy_id = f"{market_name}/{csv_file.stem}" if market_name else csv_file.stem
                strategies.append({
                    "id": strategy_id,
                    "name": csv_file.stem,
                    "filename": csv_file.name,
                    "market": market_name,
                    "stats": {
                        "total_trades": 0,
                        "total_pnl": 0,
                        "winning_trades": 0,
                        "losing_trades": 0,
                        "winrate": 0
                    },
                    "error": str(e)
                })
        
        return {
            "strategies": strategies,
            "markets": sorted(list(markets_set))
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la lecture des stratégies: {str(e)}"
        )


@router.get("/{strategy_id:path}/download")
def download_strategy_csv(strategy_id: str):
    """
    Télécharge le fichier CSV brut d'une stratégie
    Supporte les chemins avec marché (ex: NQ/Strategy1)
    """
    # Essayer d'abord avec le chemin complet (marché/stratégie)
    csv_file = NINJA_RUNS_PATH / f"{strategy_id}.csv"
    
    if not csv_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Fichier {strategy_id}.csv non trouvé"
        )
    
    return FileResponse(
        path=csv_file,
        filename=csv_file.name,
        media_type="text/csv"
    )


@router.get("/{strategy_id:path}/data")
def get_strategy_data(
    strategy_id: str,
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)")
):
    """
    Récupère les données détaillées d'une stratégie
    Peut filtrer par plage de dates
    Supporte les chemins avec marché (ex: NQ/Strategy1)
    """
    csv_file = NINJA_RUNS_PATH / f"{strategy_id}.csv"
    
    if not csv_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Fichier {strategy_id}.csv non trouvé"
        )
    
    try:
        # Lire le CSV avec détection automatique du séparateur
        df = pd.read_csv(csv_file, sep=None, engine='python')
        
        # Filtrer par date si les paramètres sont fournis
        if start_date or end_date:
            print(f"\n📅 Filtrage demandé pour {csv_file.name}: {start_date} -> {end_date}")
            
            # Chercher la colonne de date
            date_columns = [col for col in df.columns if 'heure' in col.lower() and 'sortie' in col.lower()]
            if not date_columns:
                date_columns = [col for col in df.columns if any(x in col.lower() for x in ['date', 'heure', 'time'])]
            
            if date_columns:
                date_col = date_columns[0]
                print(f"   Utilisation de la colonne: {date_col}")
                
                try:
                    # Convertir en datetime
                    df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y %H:%M:%S', errors='coerce')
                    if df[date_col].isna().all():
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    
                    print(f"   Lignes avant filtrage: {len(df)}")
                    
                    # Filtrer
                    if start_date:
                        start_dt = pd.to_datetime(start_date)
                        df = df[df[date_col] >= start_dt]
                    if end_date:
                        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)
                        df = df[df[date_col] < end_dt]
                    
                    print(f"   Lignes après filtrage: {len(df)}")
                except Exception as e:
                    print(f"   ❌ Erreur filtrage: {e}")
        
        stats = calculate_strategy_stats(df, csv_file.name)
        
        # Debug: vérifier les valeurs des colonnes problématiques
        print(f"\n🔍 Vérification des colonnes:")
        col_prix_entree = "Prix d'entrée"
        col_heure_entree = "Heure d'entrée"
        col_prix_sortie = "Prix de sortie"
        
        if col_prix_entree in df.columns:
            print(f"   Prix d'entrée - Valeurs uniques: {df[col_prix_entree].unique()[:5]}")
        else:
            print(f"   ⚠️ Colonne '{col_prix_entree}' non trouvée")
            
        if col_heure_entree in df.columns:
            print(f"   Heure d'entrée - Valeurs uniques: {df[col_heure_entree].unique()[:5]}")
        else:
            print(f"   ⚠️ Colonne '{col_heure_entree}' non trouvée")
            
        if col_prix_sortie in df.columns:
            print(f"   Prix de sortie - Valeurs uniques: {df[col_prix_sortie].unique()[:5]}")
        else:
            print(f"   ⚠️ Colonne '{col_prix_sortie}' non trouvée")
        
        # Convertir le DataFrame en liste de dictionnaires
        # Remplacer NaN et Infinity par None pour la sérialisation JSON
        df_clean = df.copy()
        df_clean = df_clean.replace([np.inf, -np.inf], None)
        df_clean = df_clean.where(pd.notna(df_clean), None)
        
        # Convertir en dictionnaire
        trades = df_clean.to_dict('records')
        
        # Nettoyer les valeurs pour s'assurer qu'elles sont JSON-compatibles
        for trade in trades:
            for key, value in trade.items():
                if isinstance(value, (np.integer, np.floating)):
                    if np.isnan(value) or np.isinf(value):
                        trade[key] = None
                    else:
                        trade[key] = float(value) if isinstance(value, np.floating) else int(value)
        
        # Générer la courbe d'équité
        pnl_col = stats.get('pnl_column')
        equity_curve = []
        if pnl_col and pnl_col in df.columns:
            # Fonction de nettoyage des valeurs PnL
            def clean_pnl_value(val):
                if pd.isna(val):
                    return None
                val_str = str(val).strip()
                val_str = val_str.replace('$', '').replace('€', '').replace(' ', '').replace(';', '')
                val_str = val_str.replace(',', '.')
                try:
                    return float(val_str)
                except:
                    return None
            
            cumulative_pnl = 0
            for idx, row in df.iterrows():
                pnl = clean_pnl_value(row[pnl_col])
                if pnl is not None and not np.isnan(pnl) and not np.isinf(pnl):
                    cumulative_pnl += pnl
                    # Vérifier que cumulative_pnl est valide
                    if not np.isnan(cumulative_pnl) and not np.isinf(cumulative_pnl):
                        equity_curve.append({
                            "trade": int(idx) + 1,
                            "equity": round(float(cumulative_pnl), 2)
                        })
        
        # Préparer la réponse et la nettoyer
        response_data = {
            "id": strategy_id,
            "name": strategy_id,
            "stats": stats,
            "trades": trades,
            "columns": list(df.columns),
            "equity_curve": equity_curve
        }
        
        # Nettoyer toutes les valeurs pour JSON
        cleaned_data = clean_for_json(response_data)
        
        return JSONResponse(content=cleaned_data)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la lecture du fichier: {str(e)}"
        )
