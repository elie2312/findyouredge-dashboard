# 📁 Structure du Projet - NQ Backtest Dashboard

## Vue d'ensemble

```
Dashboard/
├── backend/              # API FastAPI + Services de backtest
├── frontend/             # Interface Next.js + React
├── _archive/            # Fichiers archivés (non utilisés)
└── README.md            # Documentation principale
```

## 🔧 Backend (`/backend`)

### Structure

```
backend/
├── main.py                          # Point d'entrée FastAPI
├── start.py                         # Script de démarrage
├── requirements.txt                 # Dépendances Python
│
├── models/                          # Modèles Pydantic
│   ├── strategy.py                  # Modèles de stratégies
│   ├── run.py                       # Modèles de runs
│   └── ai_analyst.py                # Modèles IA Analyst
│
├── routers/                         # Routes API
│   ├── strategies.py                # GET /api/strategies
│   ├── runs.py                      # POST /api/runs, GET /api/runs/{id}
│   └── ai_analyst.py                # POST /api/ai/analyze
│
├── services/                        # Logique métier
│   ├── backtest/
│   │   ├── discover.py              # Découverte automatique des stratégies
│   │   ├── executor.py              # Exécution des backtests
│   │   └── results_parser.py        # Parsing des résultats
│   └── ai/
│       └── analyst.py               # Analyseur IA pour les backtests
│
├── strategies/                      # Scripts de stratégies de trading
│   ├── BACKTEST_15mn_1R_PARAM.py
│   ├── BACKTEST_30sec_1R_PARAM.py
│   └── ...
│
├── data/                            # Données CSV de marché
│   └── NQ_data.csv
│
├── runs/                            # Résultats des backtests
│   ├── {run_id}/
│   │   ├── config.json              # Configuration du run
│   │   ├── execution.log            # Logs d'exécution
│   │   ├── trades.csv               # Trades générés
│   │   └── results.json             # Résultats agrégés
│   └── ...
│
├── tools/                           # Scripts utilitaires
│   ├── generate_strategies_csv.py   # Génère le CSV de métadonnées
│   └── sync_strategies_catalog.py   # Synchronise le catalog JSON
│
├── strategies_catalog.json          # Catégories et tags des stratégies
├── strategies_metadata.csv          # Métadonnées personnalisables
└── STRATEGIES_METADATA_GUIDE.md     # Guide d'utilisation du CSV
```

### Fichiers Clés

| Fichier | Description | Éditable |
|---------|-------------|----------|
| `main.py` | Configuration FastAPI et routes | ⚠️ Dev |
| `strategies_catalog.json` | Catégories auto-générées | ✅ Oui |
| `strategies_metadata.csv` | Noms et descriptions personnalisés | ✅ Oui |
| `requirements.txt` | Dépendances Python | ⚠️ Dev |

## 🎨 Frontend (`/frontend`)

### Structure

```
frontend/
├── app/                             # Pages Next.js (App Router)
│   ├── page.tsx                     # Page d'accueil (/)
│   ├── run/
│   │   └── page.tsx                 # Configuration de backtest (/run)
│   ├── results/
│   │   └── [runId]/
│   │       └── page.tsx             # Résultats détaillés (/results/{id})
│   ├── history/
│   │   └── page.tsx                 # Historique des runs (/history)
│   ├── ia-analyst/
│   │   └── page.tsx                 # Chat IA Analyst (/ia-analyst)
│   ├── layout.tsx                   # Layout global
│   └── globals.css                  # Styles globaux
│
├── components/                      # Composants React réutilisables
│   ├── Header.tsx                   # En-tête avec navigation
│   ├── StatusBadge.tsx              # Badge de statut (running, completed, etc.)
│   ├── PerformanceChart.tsx         # Graphique de performance
│   ├── TradesTable.tsx              # Tableau des trades
│   └── ...
│
├── hooks/                           # Hooks React personnalisés
│   ├── useStrategies.ts             # Hook pour charger les stratégies
│   ├── useRuns.ts                   # Hook pour gérer les runs
│   └── useAIAnalyst.ts              # Hook pour l'IA Analyst
│
├── lib/                             # Utilitaires et configuration
│   ├── api.ts                       # Client API Axios
│   └── utils.ts                     # Fonctions utilitaires
│
├── types/                           # Types TypeScript
│   └── api.ts                       # Types pour l'API
│
├── public/                          # Assets statiques
│
├── package.json                     # Dépendances Node.js
├── tsconfig.json                    # Configuration TypeScript
├── tailwind.config.js               # Configuration Tailwind CSS
└── next.config.js                   # Configuration Next.js
```

### Pages Principales

| Route | Fichier | Description |
|-------|---------|-------------|
| `/` | `app/page.tsx` | Dashboard principal avec statistiques |
| `/run` | `app/run/page.tsx` | Configuration et lancement de backtest |
| `/results/{id}` | `app/results/[runId]/page.tsx` | Résultats détaillés d'un run |
| `/history` | `app/history/page.tsx` | Historique de tous les runs |
| `/ia-analyst` | `app/ia-analyst/page.tsx` | Chat IA pour analyse de données |

## 🔄 Flux de Données

### 1. Découverte des Stratégies

```
strategies/*.py
    ↓
discover.py (analyse automatique)
    ↓
strategies_catalog.json (catégories)
    ↓
strategies_metadata.csv (personnalisation)
    ↓
GET /api/strategies
    ↓
Frontend (sélection)
```

### 2. Exécution d'un Backtest

```
Frontend (/run)
    ↓
POST /api/runs
    ↓
executor.py (lance le script Python)
    ↓
runs/{run_id}/ (résultats)
    ↓
GET /api/runs/{id}/results
    ↓
Frontend (/results/{id})
```

### 3. Analyse IA

```
Frontend (/ia-analyst)
    ↓
POST /api/ai/analyze
    ↓
analyst.py (DataAnalyst)
    ↓
Réponse avec analyse
    ↓
Frontend (affichage Markdown)
```

## 🛠️ Commandes Utiles

### Backend

```bash
cd backend

# Installer les dépendances
pip install -r requirements.txt

# Démarrer le serveur
python start.py

# Générer le CSV de métadonnées
python tools/generate_strategies_csv.py .

# Synchroniser le catalog
python tools/sync_strategies_catalog.py .
```

### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer le serveur de dev
npm run dev

# Build pour production
npm run build

# Démarrer en production
npm start
```

## 📦 Dépendances Principales

### Backend
- **FastAPI** : Framework web
- **Uvicorn** : Serveur ASGI
- **Pandas** : Manipulation de données
- **NumPy** : Calculs numériques
- **Pydantic** : Validation de données

### Frontend
- **Next.js 14** : Framework React
- **React 18** : Bibliothèque UI
- **TypeScript** : Typage statique
- **Tailwind CSS** : Styling
- **Framer Motion** : Animations
- **Recharts** : Graphiques
- **Axios** : Client HTTP
- **React Query** : Gestion d'état serveur

## 🗂️ Conventions de Nommage

### Stratégies
- Format : `BACKTEST_{nom}_PARAM.py`
- Exemple : `BACKTEST_15mn_1R_PARAM.py`
- Le nom affiché est généré automatiquement : `15mn 1R`

### Runs
- ID : UUID court (8 caractères)
- Dossier : `backend/runs/{run_id}/`
- Fichiers :
  - `config.json` : Configuration
  - `execution.log` : Logs
  - `trades.csv` : Trades
  - `results.json` : Résultats

### API Routes
- Stratégies : `/api/strategies`
- Runs : `/api/runs`
- IA : `/api/ai`

## 🔐 Configuration

### Backend
- Port : `8000`
- Host : `0.0.0.0`
- CORS : `localhost:3000`, `localhost:3001`

### Frontend
- Port : `3000`
- API URL : `http://localhost:8000/api`

## 📚 Documentation

- `README.md` : Documentation principale
- `STRATEGIES_METADATA_GUIDE.md` : Guide du CSV de métadonnées
- `_archive/README.md` : Documentation des fichiers archivés
- `PROJECT_STRUCTURE.md` : Ce fichier

## 🚀 Démarrage Rapide

1. **Backend** :
   ```bash
   cd backend
   pip install -r requirements.txt
   python start.py
   ```

2. **Frontend** :
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Accès** :
   - Frontend : http://localhost:3000
   - API : http://localhost:8000
   - Docs API : http://localhost:8000/docs

## 🧹 Maintenance

### Nettoyage
- Anciens runs : Supprimer manuellement dans `backend/runs/`
- Cache : Supprimer `__pycache__/`, `.next/`, `node_modules/`
- Logs : Supprimer `*.log`

### Mise à jour
- Stratégies : Ajouter dans `backend/strategies/`, puis `python tools/generate_strategies_csv.py .`
- Dépendances : Mettre à jour `requirements.txt` et `package.json`

---

**Dernière mise à jour** : 12 octobre 2025
