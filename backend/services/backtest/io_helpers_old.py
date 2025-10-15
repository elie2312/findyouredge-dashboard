#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helpers pour la lecture et gestion des données.
Cache intelligent et optimisations I/O non-intrusives.
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import pandas as pd

class DataCache:
    """Cache intelligent pour les données OHLCV"""
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / ".cache"
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_cache_key(self, csv_path: str, filters: Dict[str, Any] = None) -> str:
        """Génère une clé de cache basée sur le fichier et les filtres"""
        csv_path = Path(csv_path)
        
        # Hash basé sur le chemin, taille et mtime
        stat = csv_path.stat()
        content_hash = f"{csv_path.name}_{stat.st_size}_{stat.st_mtime}"
        
        if filters:
            filter_str = "_".join(f"{k}={v}" for k, v in sorted(filters.items()))
            content_hash += f"_{filter_str}"
        
        return hashlib.md5(content_hash.encode()).hexdigest()[:12]
    
    def get_cached_data(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Récupère les données du cache si disponibles"""
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        
        if not cache_file.exists():
            return None
        
        try:
            return pd.read_parquet(cache_file)
        except Exception as e:
            print(f"Erreur lecture cache {cache_key}: {e}")
            # Supprimer le cache corrompu
            cache_file.unlink(missing_ok=True)
            return None
    
    def save_to_cache(self, cache_key: str, df: pd.DataFrame):
        """Sauvegarde les données dans le cache"""
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        
        try:
            df.to_parquet(cache_file, compression='snappy')
        except Exception as e:
            print(f"Erreur sauvegarde cache {cache_key}: {e}")
    
    def clear_cache(self):
        """Vide le cache"""
        for cache_file in self.cache_dir.glob("*.parquet"):
            cache_file.unlink()

class OptimizedDataLoader:
    """Chargeur de données optimisé avec cache"""
    
    def __init__(self, cache_dir: str = None, enable_cache: bool = True):
        self.cache = DataCache(cache_dir) if enable_cache else None
        self.enable_cache = enable_cache
        
    def load_ohlcv_data(self, csv_path: str, symbol_regex: str = None, 
                       date_range: Tuple[str, str] = None,
                       sample_mode: bool = False) -> pd.DataFrame:
        """
        Charge les données OHLCV avec optimisations
        
        Args:
            csv_path: Chemin vers le fichier CSV
            symbol_regex: Regex pour filtrer les symboles
            date_range: Tuple (start_date, end_date) pour filtrer les dates
            sample_mode: Si True, charge seulement un échantillon pour tests rapides
        """
        
        # Préparer les filtres pour le cache
        filters = {}
        if symbol_regex:
            filters['symbol_regex'] = symbol_regex
        if date_range:
            filters['date_range'] = f"{date_range[0]}_{date_range[1]}"
        if sample_mode:
            filters['sample'] = True
        
        # Vérifier le cache
        if self.enable_cache:
            cache_key = self.cache.get_cache_key(csv_path, filters)
            cached_df = self.cache.get_cached_data(cache_key)
            
            if cached_df is not None:
                print(f"📦 Données chargées depuis le cache ({len(cached_df):,} lignes)")
                return cached_df
        
        # Charger depuis le fichier
        print(f"📁 Chargement depuis {Path(csv_path).name}...")
        start_time = datetime.now()
        
        df = self._load_csv_optimized(csv_path, sample_mode)
        
        # Appliquer les filtres
        if symbol_regex:
            df = self._filter_symbols(df, symbol_regex)
        
        if date_range:
            df = self._filter_dates(df, date_range)
        
        # Nettoyer et optimiser
        df = self._clean_and_optimize(df)
        
        load_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Chargé {len(df):,} lignes en {load_time:.1f}s")
        
        # Sauvegarder dans le cache
        if self.enable_cache and len(df) > 0:
            self.cache.save_to_cache(cache_key, df)
            print(f"💾 Sauvegardé dans le cache: {cache_key}")
        
        return df
    
    def _load_csv_optimized(self, csv_path: str, sample_mode: bool = False) -> pd.DataFrame:
        """Charge le CSV avec optimisations"""
        
        # Paramètres optimisés pour pandas
        read_params = {
            'low_memory': False,
            'engine': 'c',  # Moteur C plus rapide
        }
        
        # Mode échantillon pour tests rapides
        if sample_mode:
            # Charger seulement les 100k premières lignes
            read_params['nrows'] = 100000
            print("🔬 Mode échantillon: 100k lignes max")
        
        try:
            df = pd.read_csv(csv_path, **read_params)
        except Exception as e:
            print(f"❌ Erreur lecture CSV: {e}")
            raise
        
        return df
    
    def _filter_symbols(self, df: pd.DataFrame, symbol_regex: str) -> pd.DataFrame:
        """Filtre les symboles selon le regex"""
        if 'symbol' not in df.columns:
            print("⚠️  Colonne 'symbol' introuvable, pas de filtrage")
            return df
        
        initial_count = len(df)
        df = df[df['symbol'].astype(str).str.match(symbol_regex, na=False)]
        
        filtered_count = len(df)
        print(f"🔍 Filtrage symboles: {initial_count:,} → {filtered_count:,} lignes")
        
        return df
    
    def _filter_dates(self, df: pd.DataFrame, date_range: Tuple[str, str]) -> pd.DataFrame:
        """Filtre les dates selon la plage"""
        timestamp_cols = ['ts_event', 'timestamp', 'datetime']
        timestamp_col = None
        
        for col in timestamp_cols:
            if col in df.columns:
                timestamp_col = col
                break
        
        if not timestamp_col:
            print("⚠️  Colonne timestamp introuvable, pas de filtrage temporel")
            return df
        
        # Convertir en datetime si nécessaire
        if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
            df[timestamp_col] = pd.to_datetime(df[timestamp_col], utc=True)
        
        start_date, end_date = date_range
        start_dt = pd.to_datetime(start_date, utc=True)
        end_dt = pd.to_datetime(end_date, utc=True)
        
        initial_count = len(df)
        df = df[(df[timestamp_col] >= start_dt) & (df[timestamp_col] <= end_dt)]
        
        filtered_count = len(df)
        print(f"📅 Filtrage dates: {initial_count:,} → {filtered_count:,} lignes")
        
        return df
    
    def _clean_and_optimize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie et optimise le DataFrame"""
        
        # Standardiser les noms de colonnes
        df = self._standardize_columns(df)
        
        # Optimiser les types de données
        df = self._optimize_dtypes(df)
        
        # Trier par timestamp et symbole
        if 'timestamp' in df.columns and 'symbol' in df.columns:
            df = df.sort_values(['timestamp', 'symbol']).reset_index(drop=True)
        
        return df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardise les noms de colonnes"""
        
        # Mapping des colonnes courantes
        column_mapping = {
            'ts_event': 'timestamp',
            'datetime': 'timestamp',
            'dt': 'timestamp',
        }
        
        # Renommer les colonnes en minuscules d'abord
        df.columns = df.columns.str.lower()
        
        # Appliquer le mapping
        df = df.rename(columns=column_mapping)
        
        # Vérifier les colonnes requises
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'symbol']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"⚠️  Colonnes manquantes: {missing_cols}")
        
        return df
    
    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimise les types de données pour réduire la mémoire"""
        
        # Convertir timestamp en datetime UTC
        if 'timestamp' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)\n        \n        # Optimiser les colonnes numériques\n        numeric_cols = ['open', 'high', 'low', 'close', 'volume']\n        for col in numeric_cols:\n            if col in df.columns:\n                df[col] = pd.to_numeric(df[col], errors='coerce')\n                \n                # Utiliser float32 au lieu de float64 si possible\n                if df[col].dtype == 'float64':\n                    # Vérifier si les valeurs tiennent dans float32\n                    min_val, max_val = df[col].min(), df[col].max()\n                    if (min_val >= -3.4e38 and max_val <= 3.4e38 and \n                        not df[col].isna().any()):\n                        df[col] = df[col].astype('float32')\n        \n        # Optimiser les symboles en catégorie\n        if 'symbol' in df.columns:\n            df['symbol'] = df['symbol'].astype('category')\n        \n        return df\n    \n    def get_data_info(self, csv_path: str) -> Dict[str, Any]:\n        \"\"\"Retourne des informations sur le fichier de données\"\"\"\n        csv_path = Path(csv_path)\n        \n        if not csv_path.exists():\n            return {'error': 'Fichier introuvable'}\n        \n        try:\n            # Informations sur le fichier\n            stat = csv_path.stat()\n            file_info = {\n                'filename': csv_path.name,\n                'size_mb': stat.st_size / (1024 * 1024),\n                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),\n            }\n            \n            # Échantillon pour analyser la structure\n            sample_df = pd.read_csv(csv_path, nrows=1000)\n            \n            data_info = {\n                'columns': list(sample_df.columns),\n                'dtypes': {col: str(dtype) for col, dtype in sample_df.dtypes.items()},\n                'sample_rows': len(sample_df),\n            }\n            \n            # Détection des symboles\n            if 'symbol' in sample_df.columns:\n                unique_symbols = sample_df['symbol'].unique()[:10]  # 10 premiers\n                data_info['symbols_sample'] = list(unique_symbols)\n            \n            # Détection de la plage temporelle\n            timestamp_cols = ['ts_event', 'timestamp', 'datetime']\n            for col in timestamp_cols:\n                if col in sample_df.columns:\n                    try:\n                        ts_series = pd.to_datetime(sample_df[col])\n                        data_info['date_range'] = {\n                            'start': ts_series.min().isoformat(),\n                            'end': ts_series.max().isoformat(),\n                            'timezone': 'UTC' if ts_series.dt.tz else 'Naive'\n                        }\n                        break\n                    except:\n                        pass\n            \n            return {**file_info, **data_info}\n            \n        except Exception as e:\n            return {'error': str(e)}\n\n# Interface simple pour Streamlit\ndef create_loader(cache_dir: str = None, enable_cache: bool = True) -> OptimizedDataLoader:\n    \"\"\"Crée un loader optimisé\"\"\"\n    return OptimizedDataLoader(cache_dir, enable_cache)\n\ndef load_data_for_backtest(csv_path: str, symbol_regex: str = None, \n                          sample_mode: bool = False) -> pd.DataFrame:\n    \"\"\"Interface simplifiée pour charger les données\"\"\"\n    loader = create_loader()\n    return loader.load_ohlcv_data(csv_path, symbol_regex, sample_mode=sample_mode)\n\nif __name__ == \"__main__\":\n    # Test du loader\n    import sys\n    \n    if len(sys.argv) < 2:\n        print(\"Usage: python io_helpers.py <csv_path> [symbol_regex]\")\n        sys.exit(1)\n    \n    csv_path = sys.argv[1]\n    symbol_regex = sys.argv[2] if len(sys.argv) > 2 else None\n    \n    loader = create_loader()\n    \n    # Informations sur le fichier\n    print(\"=== Informations fichier ===\")\n    info = loader.get_data_info(csv_path)\n    for key, value in info.items():\n        print(f\"{key}: {value}\")\n    \n    # Test de chargement\n    print(\"\\n=== Test chargement ===\")\n    df = loader.load_ohlcv_data(csv_path, symbol_regex, sample_mode=True)\n    \n    print(f\"\\nDonnées chargées:\")\n    print(f\"  Lignes: {len(df):,}\")\n    print(f\"  Colonnes: {list(df.columns)}\")\n    print(f\"  Mémoire: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB\")\n    \n    if len(df) > 0:\n        print(f\"\\nAperçu:\")\n        print(df.head())
