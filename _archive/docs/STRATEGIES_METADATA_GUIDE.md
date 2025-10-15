# 📋 Guide d'Utilisation du CSV de Métadonnées des Stratégies

## Vue d'ensemble

Le fichier `strategies_metadata.csv` permet de personnaliser les noms et descriptions des stratégies affichées dans le dashboard.

## Structure du CSV

| Colonne | Description | Éditable |
|---------|-------------|----------|
| `strategy_id` | Identifiant unique (nom du fichier sans .py) | ❌ Non |
| `auto_name` | Nom généré automatiquement | ❌ Non (info) |
| `auto_description` | Description générée automatiquement | ❌ Non (info) |
| `custom_name` | **Nom personnalisé** | ✅ Oui |
| `custom_description` | **Description personnalisée** | ✅ Oui |
| `timeframe` | Timeframe détecté | ❌ Non (info) |
| `risk_model` | Modèle de risque détecté | ❌ Non (info) |
| `category` | Catégorie (OPR, SuperTrend, etc.) | ❌ Non (info) |
| `tags` | Tags générés | ❌ Non (info) |
| `notes` | **Notes personnelles** | ✅ Oui |

## Comment Personnaliser

### 1. Générer le CSV

```bash
cd backend
python tools/generate_strategies_csv.py .
```

### 2. Ouvrir le CSV

- **Excel** : Double-cliquez sur `strategies_metadata.csv`
- **VS Code** : Installez l'extension "Edit CSV" pour une meilleure visualisation
- **Éditeur de texte** : N'importe quel éditeur (attention à l'encodage UTF-8)

### 3. Personnaliser les Stratégies

**Exemple 1 : Renommer une stratégie**
```csv
strategy_id,auto_name,custom_name,...
BACKTEST_15mn_1R_PARAM,15mn 1R,OPR 15mn 1R Optimisée,...
```
→ La stratégie s'affichera comme "OPR 15mn 1R Optimisée"

**Exemple 2 : Changer la description**
```csv
strategy_id,auto_description,custom_description,...
BACKTEST_15mn_1R_PARAM,"Stratégie 15mn 1R | ...",Ma stratégie principale pour le trading OPR avec ratio 1:1,...
```

**Exemple 3 : Ajouter des notes**
```csv
strategy_id,notes,...
BACKTEST_15mn_1R_PARAM,Stratégie testée et validée sur 6 mois de données,...
```

### 4. Sauvegarder et Appliquer

1. **Sauvegardez** le fichier CSV
2. **Redémarrez** le serveur backend :
   ```bash
   cd backend
   python start.py
   ```
3. **Rechargez** la page frontend (`http://localhost:3000/run`)

## Règles Importantes

### ✅ À Faire
- Remplir `custom_name` pour personnaliser le nom affiché
- Remplir `custom_description` pour une description plus détaillée
- Utiliser `notes` pour vos commentaires personnels
- Sauvegarder en UTF-8 pour préserver les accents

### ❌ À Éviter
- Ne pas modifier `strategy_id` (identifiant unique)
- Ne pas supprimer de lignes (sauf si vous supprimez la stratégie)
- Ne pas modifier les colonnes auto_* (elles sont écrasées à chaque régénération)

## Workflow Recommandé

### Ajout d'une Nouvelle Stratégie

1. Créez le fichier Python dans `backend/strategies/`
2. Générez le CSV : `python tools/generate_strategies_csv.py .`
3. Ouvrez le CSV et personnalisez la nouvelle ligne
4. Redémarrez le backend

### Mise à Jour du CSV

Le script `generate_strategies_csv.py` est **intelligent** :
- Il **préserve** vos personnalisations existantes (`custom_*`, `notes`)
- Il **met à jour** les valeurs auto-détectées (`auto_name`, `auto_description`, etc.)
- Il **ajoute** les nouvelles stratégies détectées

Vous pouvez donc le relancer sans perdre vos modifications !

## Exemples Concrets

### Exemple 1 : Stratégie OPR avec Nom Custom

```csv
BACKTEST_15mn_1R_PARAM,15mn 1R,"Stratégie 15mn 1R | ...",OPR 15 Minutes - Ratio 1:1,Stratégie OPR optimisée pour le trading de 15 minutes avec un ratio risque/récompense de 1:1. Testée sur 6 mois.,15 minutes,1R (Risk/Reward 1:1),OPR,"15 minutes, 1R",Version stable - Production ready
```

### Exemple 2 : Stratégie SuperTrend

```csv
BACKTEST_SuperTrend_ScaleIn_NoCut,SuperTrend ScaleIn NoCut,"Stratégie SuperTrend...",SuperTrend Scale-In v2,Stratégie avancée basée sur l'indicateur SuperTrend avec entrées progressives (scale-in) et sans sortie automatique.,Multi-timeframe,Scale-In (No Exit),SuperTrend,"Multi-timeframe, Scale-In",En phase de test - Résultats prometteurs
```

## Dépannage

### Le CSV n'est pas pris en compte
- Vérifiez que le fichier s'appelle bien `strategies_metadata.csv`
- Vérifiez qu'il est dans `backend/`
- Redémarrez le serveur backend

### Les accents sont mal affichés
- Sauvegardez le CSV en UTF-8 (pas en ANSI ou ISO-8859-1)
- Dans Excel : "Enregistrer sous" → "CSV UTF-8"

### Une stratégie n'apparaît pas
- Vérifiez que le fichier commence par `BACKTEST_`
- Régénérez le CSV : `python tools/generate_strategies_csv.py .`
- Vérifiez les logs du backend pour les erreurs

## Commandes Utiles

```bash
# Générer/mettre à jour le CSV
python tools/generate_strategies_csv.py .

# Voir les stratégies détectées
python tools/generate_strategies_csv.py . | grep "Aperçu"

# Tester la découverte
cd backend
python -c "from services.backtest.discover import get_available_strategies; print(get_available_strategies('.'))"
```

## Intégration avec le Dashboard

Les valeurs du CSV sont utilisées dans :
- **Page /run** : Sélection de stratégie (nom et description)
- **API /api/strategies** : Liste complète des stratégies
- **Filtres** : Les catégories et tags restent basés sur `strategies_catalog.json`

## Priorité des Valeurs

1. **custom_name** (si renseigné) → Affiché
2. **auto_name** (sinon) → Affiché

Même logique pour la description.

---

**Astuce** : Gardez une copie de sauvegarde de votre CSV personnalisé avant de le régénérer !
