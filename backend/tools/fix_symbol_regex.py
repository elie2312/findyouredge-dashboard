#!/usr/bin/env python3
"""Script pour ajouter SYMBOL_FILTER_REGEX aux stratégies qui l'utilisent mais ne le définissent pas"""

import re
from pathlib import Path

def fix_strategy(file_path: Path):
    """Ajoute SYMBOL_FILTER_REGEX si manquant"""
    content = file_path.read_text(encoding='utf-8')
    
    # Vérifier si la stratégie utilise SYMBOL_FILTER_REGEX
    uses_regex = re.search(r'load_data\([^,]+,\s*SYMBOL_FILTER_REGEX', content)
    has_regex = re.search(r'SYMBOL_FILTER_REGEX\s*=', content)
    
    if uses_regex and not has_regex:
        # Trouver la ligne CSV_PATH et ajouter SYMBOL_FILTER_REGEX après
        pattern = r'(CSV_PATH\s*=\s*[^\n]+\n)'
        replacement = r'\1SYMBOL_FILTER_REGEX = r"^NQ[HMUZ][0-9]$"  # NQ front month\n'
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ {file_path.name}: SYMBOL_FILTER_REGEX ajouté")
            return True
        else:
            print(f"⚠️  {file_path.name}: Pattern CSV_PATH non trouvé")
            return False
    elif has_regex:
        print(f"⏭️  {file_path.name}: Déjà OK")
        return False
    else:
        print(f"ℹ️  {file_path.name}: N'utilise pas SYMBOL_FILTER_REGEX")
        return False

def main():
    strategies_dir = Path(__file__).parent.parent / "strategies"
    
    print("🔧 Correction des stratégies...\n")
    
    fixed_count = 0
    for file_path in sorted(strategies_dir.glob("BACKTEST_*.py")):
        if fix_strategy(file_path):
            fixed_count += 1
    
    print(f"\n✅ {fixed_count} fichier(s) corrigé(s)")

if __name__ == "__main__":
    main()
