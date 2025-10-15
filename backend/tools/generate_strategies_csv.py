#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer/mettre à jour le CSV des métadonnées de stratégies.
Ce CSV permet de personnaliser les noms et descriptions des stratégies.
"""

import csv
import sys
from pathlib import Path

# Ajouter le chemin vers les services backend
BACKEND_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_PATH / "services" / "backtest"))

from discover import get_available_strategies

def generate_metadata_csv(base_path: str, output_path: str = None):
    """Génère un CSV avec toutes les stratégies et leurs métadonnées"""
    
    if output_path is None:
        output_path = Path(base_path) / "strategies_metadata.csv"
    else:
        output_path = Path(output_path)
    
    print(f"🔍 Découverte des stratégies dans {base_path}...")
    strategies = get_available_strategies(base_path)
    
    print(f"📊 {len(strategies)} stratégies trouvées")
    
    # Charger le CSV existant si présent pour préserver les personnalisations
    existing_data = {}
    if output_path.exists():
        print(f"📖 Chargement du CSV existant...")
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                strategy_id = row.get('strategy_id', '')
                if strategy_id:
                    existing_data[strategy_id] = row
    
    # Préparer les données pour le CSV
    csv_data = []
    for strategy in strategies:
        strategy_id = Path(strategy['script_path']).name.replace('.py', '')
        
        # Si la stratégie existe déjà, préserver les valeurs personnalisées
        if strategy_id in existing_data:
            row = existing_data[strategy_id]
            # Mettre à jour seulement les valeurs auto-détectées
            row['auto_name'] = strategy['name']
            row['auto_description'] = strategy['description']
            row['timeframe'] = strategy['timeframe']
            row['risk_model'] = strategy['risk_model']
            row['category'] = strategy['category']
            row['tags'] = ', '.join(strategy['tags'])
        else:
            # Nouvelle stratégie
            row = {
                'strategy_id': strategy_id,
                'auto_name': strategy['name'],
                'auto_description': strategy['description'],
                'custom_name': '',  # À remplir manuellement
                'custom_description': '',  # À remplir manuellement
                'timeframe': strategy['timeframe'],
                'risk_model': strategy['risk_model'],
                'category': strategy['category'],
                'tags': ', '.join(strategy['tags']),
                'notes': ''  # Notes personnelles
            }
        
        csv_data.append(row)
    
    # Trier par strategy_id
    csv_data.sort(key=lambda x: x['strategy_id'])
    
    # Écrire le CSV
    print(f"\n💾 Écriture du CSV dans {output_path}...")
    fieldnames = [
        'strategy_id',
        'auto_name',
        'auto_description',
        'custom_name',
        'custom_description',
        'timeframe',
        'risk_model',
        'category',
        'tags',
        'notes'
    ]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"✅ CSV généré avec succès !")
    print(f"\n📝 Instructions :")
    print(f"  1. Ouvrez {output_path} dans Excel ou un éditeur de texte")
    print(f"  2. Remplissez les colonnes 'custom_name' et 'custom_description' pour personnaliser")
    print(f"  3. Les valeurs custom_* remplacent les valeurs auto_* si elles sont renseignées")
    print(f"  4. Sauvegardez le fichier")
    print(f"  5. Redémarrez le serveur backend pour appliquer les changements")
    
    print(f"\n📊 Aperçu des stratégies :")
    for row in csv_data[:5]:
        print(f"  - {row['strategy_id']}: {row['auto_name']}")
    if len(csv_data) > 5:
        print(f"  ... et {len(csv_data) - 5} autres")

def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python generate_strategies_csv.py <base_path> [output_path]")
        print("Exemple: python generate_strategies_csv.py .")
        sys.exit(1)
    
    base_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    generate_metadata_csv(base_path, output_path)

if __name__ == "__main__":
    main()
