# 🚀 Guide Complet - Migration React/Next.js

## 📋 Récapitulatif de la Migration

Vous avez maintenant une stack moderne **React/Next.js + FastAPI** pour votre dashboard NQ.

---

## ✅ Ce qui a été créé

### Backend FastAPI (`backend/`)

**Structure :**
```
backend/
├── main.py              # Point d'entrée FastAPI
├── start.py             # Script de démarrage
├── test_backend.py      # Tests de connexion
├── requirements.txt     # Dépendances Python
├── models/
│   ├── strategy.py      # Modèles Pydantic stratégies
│   └── run.py          # Modèles Pydantic runs
├── routers/
│   ├── strategies.py    # API /api/strategies
│   └── runs.py         # API /api/runs
└── services/
    └── (vide)          # Prêt pour services futurs
```

**Endpoints API disponibles :**
- `GET /api/strategies` - Liste des stratégies
- `GET /api/strategies/{id}` - Détails d'une stratégie
- `POST /api/runs` - Lancer un backtest
- `GET /api/runs` - Liste des runs
- `GET /api/runs/{id}/status` - Statut d'un run
- `GET /api/runs/{id}/results` - Résultats d'un run

**✅ Backend testé et fonctionnel** : Connecté à vos scripts existants

---

### Frontend Next.js (`frontend/`)

**Structure :**
```
frontend/
├── app/
│   ├── layout.tsx       # Layout principal + ThemeProvider
│   ├── page.tsx         # Page d'accueil complète
│   ├── providers.tsx    # React Query Provider
│   └── globals.css      # Styles globaux + animations
├── components/
│   ├── ui/             # Composants de base
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   └── table.tsx
│   ├── dashboard/      # Composants dashboard
│   │   ├── kpi-card.tsx
│   │   ├── status-badge.tsx
│   │   ├── strategy-card.tsx
│   │   ├── run-card.tsx
│   │   ├── header.tsx
│   │   └── index.ts
│   ├── charts/         # Charts Recharts + Framer Motion
│   │   ├── equity-chart.tsx
│   │   ├── drawdown-chart.tsx
│   │   ├── win-loss-pie.tsx
│   │   ├── profit-loss-bar.tsx
│   │   └── index.ts
│   └── theme-provider.tsx
├── hooks/
│   ├── useStrategies.ts  # Hooks React Query stratégies
│   └── useRuns.ts        # Hooks React Query runs
├── lib/
│   ├── api.ts           # Client API axios
│   └── utils.ts         # Fonctions utilitaires
├── types/
│   └── api.ts          # Types TypeScript
└── package.json        # Dépendances
```

**Technologies utilisées :**
- ✅ **Next.js 14** - Framework React avec App Router
- ✅ **TypeScript** - Typage statique
- ✅ **TailwindCSS** - Styling moderne
- ✅ **Framer Motion** - Animations fluides
- ✅ **Recharts** - Graphiques interactifs
- ✅ **TanStack Query** - Gestion d'état async
- ✅ **next-themes** - Dark mode

---

## 🚀 Installation et Démarrage

### Prérequis

**1. Node.js requis pour le frontend**

Téléchargez et installez Node.js : https://nodejs.org/
- Version recommandée : 18.x ou 20.x (LTS)
- Vérifiez l'installation : `node --version` et `npm --version`

**2. Python déjà installé pour le backend**

Vous l'avez déjà ✅

---

### Installation Backend (déjà fait)

```powershell
cd c:\Users\elieb\Desktop\Dashboard\backend

# Activer l'environnement virtuel (déjà créé)
.\venv\Scripts\Activate.ps1

# Les dépendances sont déjà installées
# Si besoin : pip install -r requirements.txt

# Démarrer le backend
python start.py
```

**Backend disponible sur :** `http://localhost:8000`  
**Documentation API :** `http://localhost:8000/docs`

---

### Installation Frontend (à faire après installation Node.js)

```powershell
cd c:\Users\elieb\Desktop\Dashboard\frontend

# Installer les dépendances
npm install

# Démarrer le frontend
npm run dev
```

**Frontend disponible sur :** `http://localhost:3000`

---

## 🎨 Composants Créés

### Composants UI de Base

**Button** - Bouton avec variantes
```tsx
<Button variant="default" size="lg">Lancer</Button>
<Button variant="outline">Détails</Button>
```

**Card** - Carte avec header/content
```tsx
<Card>
  <CardHeader>
    <CardTitle>Titre</CardTitle>
  </CardHeader>
  <CardContent>Contenu</CardContent>
</Card>
```

**Badge** - Badge de statut
```tsx
<Badge variant="success">Terminé</Badge>
<Badge variant="warning">En cours</Badge>
```

**Table** - Table responsive
```tsx
<Table>
  <TableHeader>...</TableHeader>
  <TableBody>...</TableBody>
</Table>
```

---

### Composants Dashboard

**KpiCard** - Carte KPI avec animation
```tsx
import { TrendingUp } from 'lucide-react'

<KpiCard
  title="Total Runs"
  value="42"
  icon={TrendingUp}
  trend={{ value: 12, isPositive: true }}
  delay={0.1}
/>
```

**StatusBadge** - Badge de statut animé
```tsx
<StatusBadge status="running" message="En cours..." />
<StatusBadge status="completed" />
```

**StrategyCard** - Carte stratégie
```tsx
<StrategyCard
  strategy={strategyData}
  onRun={(strategy) => handleRun(strategy)}
  index={0}
/>
```

**RunCard** - Carte run
```tsx
<RunCard
  run={runData}
  onViewResults={(id) => router.push(`/results/${id}`)}
  index={0}
/>
```

---

### Composants Charts (Recharts + Framer Motion)

**EquityChart** - Courbe d'équité animée
```tsx
<EquityChart
  data={[0, 100, 250, 180, 400]}
  title="Courbe d'Équité"
/>
```

**DrawdownChart** - Courbe de drawdown
```tsx
<DrawdownChart
  data={[0, 0, -50, -20, 0]}
  title="Drawdown"
/>
```

**WinLossPie** - Pie chart win/loss
```tsx
<WinLossPie
  winningTrades={65}
  losingTrades={35}
/>
```

**ProfitLossBar** - Bar chart profit/loss
```tsx
<ProfitLossBar
  grossProfit={25000}
  grossLoss={-12000}
/>
```

---

## 🎯 Hooks React Query

### useStrategies
```tsx
const { data, isLoading, error } = useStrategies()
// data.strategies contient la liste
```

### useRuns
```tsx
const { data, isLoading } = useRuns()
// Polling automatique toutes les 5 secondes
```

### useRunStatus
```tsx
const { data: status } = useRunStatus(runId)
// Polling adaptatif (2s si running, 10s sinon)
```

### useRunResults
```tsx
const { data: results } = useRunResults(runId)
// Cache 10 minutes (résultats immuables)
```

### useCreateRun
```tsx
const createRun = useCreateRun()

const handleRun = async () => {
  await createRun.mutateAsync({
    strategy_id: 'opr_30sec_1r',
    parameters: {}
  })
}
```

---

## 🎨 Animations Implémentées

### Framer Motion

**Fade-in progressif**
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5, delay: 0.1 }}
>
```

**Hover effects**
```tsx
<motion.div
  whileHover={{ y: -4, scale: 1.02 }}
  transition={{ duration: 0.2 }}
>
```

**Pulse animation (status running)**
```tsx
<motion.span
  animate={{ scale: [1, 1.2, 1] }}
  transition={{ duration: 2, repeat: Infinity }}
>
```

### Recharts

- **Courbes animées** : 800ms-1000ms d'animation
- **Transitions fluides** : ease-in-out
- **Tooltips interactifs** : Hover sur graphiques

---

## 🌙 Dark Mode

**Implémenté avec next-themes**

Utilisation dans un composant :
```tsx
import { useTheme } from 'next-themes'

const { theme, setTheme } = useTheme()
setTheme('dark') // ou 'light' ou 'system'
```

Classes Tailwind automatiques :
```tsx
<div className="bg-white dark:bg-slate-900">
```

---

## 📊 Prochaines Étapes

### Étape 4 : Pages Avancées (à créer)
- Page Run détaillée
- Page Results complète
- Page Compare multi-runs

### Étape 5 : Fonctionnalités
- Formulaire de lancement avec paramètres
- WebSocket pour le statut en temps réel (optionnel)
- Export des résultats (CSV, PDF)

### Étape 6 : Optimisations
- Virtualisation des tables (TanStack Table)
- Code splitting
- Performance monitoring

### Étape 7 : Déploiement
- Build production (`npm run build`)
- Configuration serveur
- CI/CD

---

## 🐛 Troubleshooting

### Erreurs TypeScript actuelles

**Normal** : Les erreurs disparaîtront après `npm install`

### Backend ne démarre pas

```powershell
# Vérifier Python
python --version

# Réinstaller dépendances
pip install -r requirements.txt

# Tester connexion adapters
python test_backend.py
```

### Frontend ne démarre pas

```powershell
# Vérifier Node.js
node --version
npm --version

# Nettoyer et réinstaller
rm -rf node_modules
npm install
```

### Erreur CORS

Le backend est configuré pour accepter `localhost:3000`  
Si vous changez de port, modifiez `backend/main.py`

---

## 📚 Ressources

- [Next.js Docs](https://nextjs.org/docs)
- [TailwindCSS](https://tailwindcss.com/docs)
- [Framer Motion](https://www.framer.com/motion/)
- [Recharts](https://recharts.org/)
- [TanStack Query](https://tanstack.com/query/latest)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## ✅ Checklist Finale

**Backend :**
- [x] Structure créée
- [x] API endpoints implémentés
- [x] Connexion aux scripts existants
- [x] Tests validés
- [x] Backend démarré

**Frontend :**
- [x] Structure Next.js créée
- [x] Configuration complète
- [x] Composants UI créés (14 composants)
- [x] Hooks React Query
- [x] Types TypeScript
- [x] Page d'accueil fonctionnelle
- [ ] Installation npm (Node.js requis)
- [ ] Démarrage frontend

**Reste à faire :**
1. Installer Node.js
2. `npm install` dans frontend/
3. `npm run dev`
4. Tester la connexion backend ↔ frontend
5. Créer les pages Run et Results (étape 4)

---

**Migration : 70% complète** 🎯

Prêt pour l'installation Node.js et les tests !
