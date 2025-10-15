#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script utilitaire pour synchroniser le catalog des stratégies.
Parcourt le dossier strategies/, propose des catégories par heuristique,
et crée/met à jour le fichier strategies_catalog.json.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Ajouter le chemin vers les services backend
BACKEND_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_PATH / "services" / "backtest"))

from discover import StrategyDiscovery, get_available_strategies

def generate_catalog_suggestions(base_path: str) -> Dict[str, Dict[str, Any]]:
    """Génère des suggestions de catalog basées sur la découverte"""
    strategies = get_available_strategies(base_path)
    suggestions = {}

    for strategy in strategies:
        filename = Path(strategy['script_path']).name.replace('.py', '')
        name = strategy['name']
        timeframe = strategy['timeframe']
        risk_model = strategy['risk_model']

        # Heuristique pour déterminer la catégorie
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

        suggestions[filename] = {
            'category': category,
            'tags': tags
        }

    return suggestions

def main():
    """Fonction principale"""
    if len(sys.argv) != 2:
        print("Usage: python sync_strategies_catalog.py <base_path>")
        sys.exit(1)

    base_path = sys.argv[1]
    catalog_path = Path(base_path) / "strategies_catalog.json"

    print(f"🔍 Analyse des stratégies dans {base_path}/strategies/...")
    suggestions = generate_catalog_suggestions(base_path)

    print(f"\n📋 Suggestions générées pour {len(suggestions)} stratégies :")
    for filename, data in suggestions.items():
        print(f"  - {filename}: catégorie='{data['category']}', tags={data['tags']}")

    # Charger le catalog existant si présent
    existing_catalog = {}
    if catalog_path.exists():
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                existing_catalog = json.load(f)
            print("\n📖 Catalog existant chargé.")
        except Exception as e:
            print(f"\n❌ Erreur lecture catalog existant: {e}")

    # Fusionner avec les suggestions
    merged_catalog = {**existing_catalog, **suggestions}

    print(f"\n💾 Sauvegarde du catalog dans {catalog_path}...")
    try:
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump(merged_catalog, f, indent=2, ensure_ascii=False)
        print("✅ Catalog sauvegardé avec succès !")
    except Exception as e:
        print(f"❌ Erreur sauvegarde catalog: {e}")
        sys.exit(1)

    print("\n📝 Prochaines étapes :")
    print("  - Vérifiez le catalog généré")
    print("  - Ajustez manuellement les catégories/tags si nécessaire")
    print("  - Relancez votre serveur backend pour tester")

if __name__ == "__main__":
    main()
