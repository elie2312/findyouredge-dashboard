#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour mettre à jour tous les chemins CSV_PATH dans les stratégies
pour utiliser la configuration centralisée
"""

import re
from pathlib import Path

def update_strategy_file(file_path: Path):
    """Met à jour un fichier de stratégie pour utiliser config.py"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si déjà mis à jour
    if 'from config import DATA_CSV_FULL_PATH' in content:
        print(f"   ⏭️  {file_path.name} - Déjà à jour")
        return False
    
    # Pattern pour trouver la section d'imports
    import_section_pattern = r'(from datetime import[^\n]+\n)'
    
    # Ajouter les imports nécessaires
    new_imports = '''import sys
from pathlib import Path

# Ajouter le chemin du backend pour importer config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_CSV_FULL_PATH

'''
    
    # Remplacer la ligne CSV_PATH
    csv_path_pattern = r'CSV_PATH\s*=\s*r?"[^"]+"\s*#?.*'
    new_csv_path = 'CSV_PATH = str(DATA_CSV_FULL_PATH)  # Chargé depuis config.py'
    
    # Appliquer les modifications
    modified = False
    
    # 1. Ajouter les imports après "from datetime import..."
    if re.search(import_section_pattern, content):
        content = re.sub(
            import_section_pattern,
            r'\1' + new_imports,
            content,
            count=1
        )
        modified = True
    
    # 2. Remplacer CSV_PATH
    if re.search(csv_path_pattern, content):
        content = re.sub(
            csv_path_pattern,
            new_csv_path,
            content
        )
        modified = True
    
    if modified:
        # Sauvegarder
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ {file_path.name} - Mis à jour")
        return True
    else:
        print(f"   ⚠️  {file_path.name} - Aucune modification nécessaire")
        return False

def main():
    """Fonction principale"""
    backend_path = Path(__file__).parent.parent
    strategies_dir = backend_path / "strategies"
    
    print("🔄 Mise à jour des chemins CSV dans les stratégies...\n")
    
    # Trouver tous les fichiers BACKTEST_*.py
    strategy_files = list(strategies_dir.glob("BACKTEST_*.py"))
    
    if not strategy_files:
        print("❌ Aucun fichier de stratégie trouvé")
        return
    
    print(f"📊 {len(strategy_files)} stratégies trouvées\n")
    
    updated_count = 0
    for file_path in sorted(strategy_files):
        if update_strategy_file(file_path):
            updated_count += 1
    
    print(f"\n✅ Terminé: {updated_count}/{len(strategy_files)} fichiers mis à jour")
    
    if updated_count > 0:
        print("\n💡 Les stratégies utilisent maintenant le chemin depuis backend/config.py")
        print("   Pour changer le fichier de données, modifiez backend/.env")

if __name__ == "__main__":
    main()
