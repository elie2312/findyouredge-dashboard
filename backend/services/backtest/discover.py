#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-découverte des stratégies de backtest disponibles.
Introspection non-intrusive du code existant.
"""

import re
import ast
import inspect
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class StrategyInfo:
    """Métadonnées d'une stratégie détectée"""
    name: str
    script_path: Path
    description: str
    parameters: Dict[str, Any]
    output_files: List[str]
    timeframe: str
    risk_model: str
    category: str
    tags: List[str]


class StrategyDiscovery:
    """Découverte automatique des stratégies dans le dossier strategies/"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.backtests_dir = self.base_path / "strategies"
        self.catalog_path = self.base_path / "strategies_catalog.json"
        self.metadata_csv_path = self.base_path / "strategies_metadata.csv"
        self.catalog = self._load_catalog()
        self.metadata_overrides = self._load_metadata_csv()
        
    def _load_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Charge le catalog des stratégies depuis le fichier JSON"""
        if self.catalog_path.exists():
            try:
                with open(self.catalog_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur chargement catalog: {e}")
        return {}
    
    def _load_metadata_csv(self) -> Dict[str, Dict[str, str]]:
        """Charge les métadonnées personnalisées depuis le CSV"""
        if not self.metadata_csv_path.exists():
            return {}
        
        try:
            import csv
            metadata = {}
            with open(self.metadata_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    strategy_id = row.get('strategy_id', '')
                    if strategy_id:
                        metadata[strategy_id] = {
                            'custom_name': row.get('custom_name', ''),
                            'custom_description': row.get('custom_description', ''),
                            'notes': row.get('notes', '')
                        }
            return metadata
        except Exception as e:
            print(f"Erreur chargement metadata CSV: {e}")
            return {}
    
    def discover_all(self) -> List[StrategyInfo]:
        """Découvre toutes les stratégies disponibles"""
        strategies = []
        
        if not self.backtests_dir.exists():
            return strategies
            
        for script_file in self.backtests_dir.glob("BACKTEST_*.py"):
            try:
                strategy = self._analyze_script(script_file)
                if strategy:
                    strategies.append(strategy)
            except Exception as e:
                print(f"Erreur analyse {script_file.name}: {e}")
                
        return sorted(strategies, key=lambda s: s.name)
        
    def discover_all(self) -> List[StrategyInfo]:
        """Découvre toutes les stratégies disponibles"""
        strategies = []
        
        if not self.backtests_dir.exists():
            return strategies
            
        for script_file in self.backtests_dir.glob("BACKTEST_*.py"):
            try:
                strategy = self._analyze_script(script_file)
                if strategy:
                    strategies.append(strategy)
            except Exception as e:
                print(f"Erreur analyse {script_file.name}: {e}")
                
        return sorted(strategies, key=lambda s: s.name)
    
    def _analyze_script(self, script_path: Path) -> Optional[StrategyInfo]:
        """Analyse un script pour extraire ses métadonnées"""
        try:
            content = script_path.read_text(encoding='utf-8')
            
            # Extraction du nom de stratégie depuis le nom de fichier
            name = self._extract_strategy_name(script_path.name)
            
            # Analyse des paramètres de configuration
            params = self._extract_parameters(content)
            
            # Extraction des fichiers de sortie
            output_files = self._extract_output_files(content)
            
            # Détection du timeframe
            timeframe = self._detect_timeframe(script_path.name, content)
            
            # Détection du modèle de risque
            risk_model = self._detect_risk_model(script_path.name, content)
            
            # Description générée
            description = self._generate_description(name, timeframe, risk_model, params)
            
            # Récupération de la catégorie et des tags depuis le catalog ou déduction
            category, tags = self._get_category_and_tags(script_path.name, name, timeframe, risk_model)
            
            # Appliquer les overrides depuis le CSV si présents
            strategy_id = script_path.name.replace('.py', '')
            if strategy_id in self.metadata_overrides:
                overrides = self.metadata_overrides[strategy_id]
                if overrides.get('custom_name'):
                    name = overrides['custom_name']
                if overrides.get('custom_description'):
                    description = overrides['custom_description']
            
            return StrategyInfo(
                name=name,
                script_path=script_path,
                description=description,
                parameters=params,
                output_files=output_files,
                timeframe=timeframe,
                risk_model=risk_model,
                category=category,
                tags=tags
            )
            
        except Exception as e:
            print(f"Erreur parsing {script_path.name}: {e}")
            return None
    
    def _extract_strategy_name(self, filename: str) -> str:
        """Extrait un nom lisible depuis le nom de fichier"""
        # BACKTEST_30sec_1R_PARAM.py -> 30sec 1R
        # Enlever BACKTEST_ et _PARAM.py (ou juste .py)
        name = filename.replace('BACKTEST_', '').replace('_PARAM.py', '').replace('.py', '')
        # Remplacer les underscores par des espaces
        name = name.replace('_', ' ')
        
        # Formatage spécial pour les patterns courants (optionnel)
        name = re.sub(r'(\d+)(sec|mn)', r'\1\2', name)
        name = re.sub(r'(\d+)R', r'\1R', name)
        
        return name
    
    def _extract_parameters(self, content: str) -> Dict[str, Any]:
        """Extrait les paramètres configurables du script"""
        params = {}
        
        # Patterns pour détecter les variables de configuration
        config_patterns = [
            r'^([A-Z_]+)\s*=\s*([^#\n]+)',  # VARIABLE = valeur
            r'^#\s*([A-Za-z_]+)\s*=\s*([^#\n]+)',  # # variable = valeur (commenté)
        ]
        
        for pattern in config_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                var_name = match.group(1).strip()
                var_value = match.group(2).strip()
                
                # Filtrer les variables de configuration pertinentes
                if self._is_config_variable(var_name):
                    params[var_name] = self._parse_value(var_value)
        
        return params
    
    def _is_config_variable(self, var_name: str) -> bool:
        """Détermine si une variable est un paramètre de configuration"""
        config_vars = {
            'OPR_SECONDS', 'TICK_SIZE', 'POINT_VALUE', 'ENTRY_BUFFER_TICKS',
            'MIN_STOP_POINTS', 'MAX_RISK_USD', 'NQ_MIN', 'NQ_MAX',
            'SLIPPAGE_TICKS', 'COMMISSION_RT', 'MAX_TRADES_PER_DAY',
            'OPR_MIN_WIDTH_PTS', 'OPR_START_UTC', 'FLAT_TIME_UTC',
            # SuperTrend parameters
            'ATR_PERIOD', 'MULTIPLIER', 'RISK_PER_TRADE_USD',
            'MAX_CONTRACTS_TOTAL', 'MAX_SCALE_IN_COUNT'
        }
        return var_name in config_vars
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse une valeur de configuration"""
        value_str = value_str.strip().rstrip(',')
        
        try:
            # Essayer d'évaluer comme littéral Python
            return ast.literal_eval(value_str)
        except:
            # Si échec, retourner comme string
            return value_str.strip('"\'')
    
    def _extract_output_files(self, content: str) -> List[str]:
        """Extrait les noms des fichiers de sortie"""
        output_files = []
        
        # Chercher les variables OUTPUT_*_CSV
        pattern = r'OUTPUT_[A-Z_]*CSV\s*=\s*["\']([^"\'\n]+)["\']'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            filename = match.group(1)
            output_files.append(filename)
            
        return output_files
    
    def _detect_timeframe(self, filename: str, content: str) -> str:
        """Détecte le timeframe de la stratégie"""
        if '30sec' in filename.lower():
            return '30 secondes'
        elif '15mn' in filename.lower():
            return '15 minutes'
        elif '1mn' in filename.lower():
            return '1 minute'
        elif '5mn' in filename.lower():
            return '5 minutes'
        
        # Chercher dans le contenu
        if 'OPR_SECONDS' in content:
            match = re.search(r'OPR_SECONDS\s*=\s*(\d+)', content)
            if match:
                seconds = int(match.group(1))
                if seconds < 60:
                    return f'{seconds} secondes'
                else:
                    return f'{seconds//60} minutes'
        
        # Pour les stratégies non-OPR (comme SuperTrend)
        if 'SuperTrend' in filename or 'ScaleIn' in filename:
            return 'Multi-timeframe'
        
        return 'Non détecté'
    
    def _detect_risk_model(self, filename: str, content: str) -> str:
        """Détecte le modèle de risque utilisé"""
        if '1R' in filename:
            return '1R (Risk/Reward 1:1)'
        elif '5R' in filename:
            return '5R (Risk/Reward 1:5)'
        elif '10R' in filename:
            return '10R (Risk/Reward 1:10)'
        
        # SuperTrend ScaleIn
        if 'ScaleIn' in filename and 'NoCut' in filename:
            return 'Scale-In (No Exit)'
        
        # Chercher dans le contenu pour des patterns de TP
        if 'tp_pts' in content.lower():
            return 'Risk/Reward variable'
        
        if 'RISK_PER_TRADE_USD' in content:
            return 'Risque fixe par trade'
        
        return 'Modèle standard'
    
    def _generate_description(self, name: str, timeframe: str, risk_model: str, params: Dict) -> str:
        """Génère une description de la stratégie"""
        desc_parts = []
        
        desc_parts.append(f"Stratégie {name}")
        
        if timeframe != 'Non détecté':
            desc_parts.append(f"Timeframe: {timeframe}")
            
        if risk_model != 'Modèle standard':
            desc_parts.append(f"Risque: {risk_model}")
            
        if 'MAX_RISK_USD' in params:
            desc_parts.append(f"Risque max: ${params['MAX_RISK_USD']:,.0f}")
            
        return ' | '.join(desc_parts)

    def _get_category_and_tags(self, filename: str, name: str, timeframe: str, risk_model: str) -> tuple[str, List[str]]:
        """Récupère la catégorie et les tags depuis le catalog ou par déduction"""
        # Clé du catalog basée sur le nom de fichier
        catalog_key = filename.replace('.py', '')
        
        if catalog_key in self.catalog:
            # Récupérer depuis le catalog
            catalog_entry = self.catalog[catalog_key]
            category = catalog_entry.get('category', 'Autres')
            tags = catalog_entry.get('tags', [])
        else:
            # Déduction par nommage si pas dans le catalog
            if 'SuperTrend' in name or 'ScaleIn' in name or 'NoCut' in name:
                category = 'SuperTrend'
                tags = ['Multi-timeframe', 'Scale-In']
            elif 'SimpleCandle' in name:
                category = 'SimpleCandle'
                tags = ['30 minutes', 'SimpleCandle']
            elif 'OPR' in name or '30sec' in filename or '15mn' in filename:
                category = 'OPR'
                tags = [timeframe, risk_model]
            else:
                category = 'Autres'
                tags = ['Non catégorisé']
        
        return category, tags

def get_available_strategies(base_path: str) -> List[Dict[str, Any]]:
    """Interface simple pour Streamlit"""
    discovery = StrategyDiscovery(Path(base_path))
    strategies = discovery.discover_all()
    
    return [
        {
            'name': s.name,
            'script_path': str(s.script_path),
            'description': s.description,
            'parameters': s.parameters,
            'timeframe': s.timeframe,
            'risk_model': s.risk_model,
            'category': s.category,
            'tags': s.tags,
            'output_files': s.output_files
        }
        for s in strategies
    ]

if __name__ == "__main__":
    # Test de découverte
    import sys
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    strategies = get_available_strategies(base_path)
    
    print(f"\n=== Stratégies découvertes ({len(strategies)}) ===")
    for strategy in strategies:
        print(f"\n📊 {strategy['name']}")
        print(f"   📁 {Path(strategy['script_path']).name}")
        print(f"   📝 {strategy['description']}")
        print(f"   ⚙️  {len(strategy['parameters'])} paramètres configurables")
        if strategy['output_files']:
            print(f"   📄 Sorties: {', '.join(strategy['output_files'])}")
