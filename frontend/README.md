# NQ Backtest Dashboard - Frontend

Frontend Next.js 14 pour le dashboard de backtesting NQ.

## Installation

```bash
npm install
```

## Démarrage

### 1. Démarrer le backend (dans un terminal séparé)
```bash
cd ../backend
python start.py
```

Le backend sera disponible sur `http://localhost:8000`

### 2. Démarrer le frontend
```bash
npm run dev
```

Le frontend sera disponible sur `http://localhost:3000`

## Stack Technique

- **Next.js 14** - Framework React avec App Router
- **TypeScript** - Typage statique
- **TailwindCSS** - Styling
- **Framer Motion** - Animations
- **TanStack Query** - Gestion d'état asynchrone
- **Recharts** - Graphiques
- **Axios** - Client HTTP

## Structure

```
frontend/
├── app/                  # Pages Next.js (App Router)
│   ├── layout.tsx       # Layout principal
│   ├── page.tsx         # Page d'accueil
│   ├── providers.tsx    # Providers React Query
│   └── globals.css      # Styles globaux
├── components/          # Composants React réutilisables
├── hooks/              # Custom hooks
│   ├── useStrategies.ts
│   └── useRuns.ts
├── lib/                # Utilitaires
│   └── api.ts          # Client API
└── types/              # Types TypeScript
    └── api.ts
```

## API Backend

Le frontend communique avec le backend FastAPI sur `http://localhost:8000/api`

Endpoints disponibles :
- `GET /api/strategies` - Liste des stratégies
- `POST /api/runs` - Lancer un backtest
- `GET /api/runs` - Liste des runs
- `GET /api/runs/:id/status` - Statut d'un run
- `GET /api/runs/:id/results` - Résultats d'un run
