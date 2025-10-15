# 📦 Archive - Dashboard NQ Backtest

Ce dossier contient les fichiers archivés qui ne sont plus utilisés dans le projet actif.

**Date d'archivage** : 12 octobre 2025

## 📂 Structure

### `backend_tests/`
Fichiers de test temporaires créés pendant le développement :
- `test_api.py` - Tests de l'API
- `test_debug.py` - Script de debug pour les stratégies
- `test_discovery.py` - Tests du système de découverte
- `test_simple_discovery.py` - Tests simplifiés
- `test_strategy_categorization.py` - Tests de catégorisation

**Raison** : Ces fichiers étaient des scripts de test ad-hoc. Les vrais tests devraient être dans un dossier `tests/` structuré.

### `backend_check_scripts/`
Scripts de vérification one-shot :
- `check_all_strategies.py`
- `check_close_discovery.py`
- `check_strategy_id.py`
- `check_trades.py`

**Raison** : Scripts utilisés ponctuellement pour vérifier des données. Peuvent être utiles pour référence future.

### `backend_old_csv/`
Fichiers CSV générés par d'anciens backtests :
- `close30_trades.csv`
- `front_month_selection_log*.csv`
- `opr_trades*.csv`
- `supertrend_scalein_trades.csv`
- `test_simple_trades.csv`
- `strategies_metadata.~csv` (fichier temporaire)

**Raison** : Résultats de backtests obsolètes. Les nouveaux résultats sont dans `backend/runs/`.

### Fichiers racine
- `debug.log` - Ancien fichier de logs
- `.pytest_cache/` - Cache pytest

## ⚠️ Important

**Ne supprimez pas ces fichiers** sans vérifier qu'ils ne contiennent pas de données importantes.

Si vous avez besoin de restaurer un fichier :
1. Copiez-le depuis `_archive/` vers son emplacement d'origine
2. Vérifiez qu'il fonctionne toujours avec la version actuelle du code

## 🔄 Restauration

Pour restaurer un fichier :
```bash
# Exemple : restaurer un script de test
Copy-Item "_archive/backend_tests/test_debug.py" "backend/"
```

## 🗑️ Suppression Sécurisée

Si vous êtes sûr de ne plus avoir besoin de ces fichiers après quelques semaines :
```bash
# Supprimer tout l'archive (ATTENTION : irréversible)
Remove-Item -Recurse -Force "_archive"
```

## 📝 Notes

- Les fichiers actifs du projet sont dans `backend/` et `frontend/`
- Les résultats de backtests actifs sont dans `backend/runs/`
- Le CSV de métadonnées actif est `backend/strategies_metadata.csv`
- Les stratégies actives sont dans `backend/strategies/`

---

**Conseil** : Gardez cet archive pendant au moins 1 mois avant de le supprimer définitivement.
