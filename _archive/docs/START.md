# 🚀 Démarrage Rapide - NQ Dashboard

## ⚡ Commandes Essentielles

### 1️⃣ Démarrer le Backend (Prêt maintenant)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python start.py
```

✅ **Backend disponible sur :** `http://localhost:8000`  
📚 **Documentation API :** `http://localhost:8000/docs`

---

### 2️⃣ Démarrer le Frontend (après installation Node.js)

**Première fois :**
```powershell
cd frontend
npm install          # Installer les dépendances (5-10 min)
npm run dev          # Lancer le serveur de développement
```

**Prochaines fois :**
```powershell
cd frontend
npm run dev
```

✅ **Frontend disponible sur :** `http://localhost:3000`

---

## 📦 Prérequis

### Backend ✅
- [x] Python 3.x (déjà installé)
- [x] FastAPI + Uvicorn (déjà installé)
- [x] Connexion aux scripts NQ (validée)

### Frontend ⏳
- [ ] **Node.js** (à installer)
  - Télécharger : https://nodejs.org/
  - Version recommandée : 18.x ou 20.x LTS
  - Vérifier installation : `node --version` et `npm --version`

---

## 🧪 Tester la Connexion

### Backend
```powershell
# Dans un navigateur
http://localhost:8000/

# Ou avec curl
curl http://localhost:8000/
```

**Résultat attendu :**
```json
{
  "status": "ok",
  "service": "NQ Backtest API",
  "version": "1.0.0"
}
```

### Frontend
```powershell
# Ouvrir dans un navigateur
http://localhost:3000/
```

**Résultat attendu :**
- Page d'accueil avec header "🚀 NQ Backtest Dashboard"
- 4 KPI cards en haut
- Liste des stratégies
- Exécutions récentes

---

## 🎯 Fonctionnalités Disponibles

### Page d'Accueil (/)
- Vue d'ensemble des statistiques
- Liste des stratégies disponibles
- Exécutions récentes

### Page Run (/run)
- Sélection de stratégie
- Configuration des paramètres
- Lancement de backtest
- Suivi en temps réel

### Page Results (/results/[runId])
- Métriques de performance (8 KPIs)
- Courbes d'équité et drawdown
- Graphiques Win/Loss et Profit/Loss
- Table des trades
- Téléchargement des fichiers

### Page Compare (/compare)
- Sélection multi-runs
- Comparaison côte à côte
- Export des résultats

---

## 🐛 Troubleshooting

### Erreur : Port 8000 déjà utilisé

```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

### Erreur : Port 3000 déjà utilisé

```powershell
# Trouver le processus
netstat -ano | findstr :3000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

### Frontend : Erreurs TypeScript

**Normal avant `npm install`**

Les erreurs TypeScript disparaîtront automatiquement après :
```powershell
npm install
```

### Backend : Module non trouvé

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🎨 Thème et Personnalisation

### Changer le Thème

Le dashboard supporte le **dark mode**. Cliquez sur l'icône 🌙/☀️ dans le header.

### Modifier les Couleurs

Éditez `frontend/app/globals.css` :

```css
:root {
  --primary: 221.2 83.2% 53.3%;  /* Bleu par défaut */
  /* Modifier ces valeurs HSL */
}
```

---

## 📊 Endpoints API Disponibles

### Stratégies
- `GET /api/strategies` - Liste des stratégies
- `GET /api/strategies/{id}` - Détails d'une stratégie

### Runs
- `POST /api/runs` - Lancer un backtest
- `GET /api/runs` - Liste des runs
- `GET /api/runs/{id}/status` - Statut d'un run
- `GET /api/runs/{id}/results` - Résultats d'un run

---

## 🔥 Commandes Utiles

### Backend

```powershell
# Tester la connexion aux adapters
python backend/test_backend.py

# Redémarrer le backend
# Ctrl+C puis
python backend/start.py
```

### Frontend

```powershell
# Build de production
npm run build

# Lancer en mode production
npm run start

# Linter
npm run lint
```

---

## 📁 Fichiers Importants

### Configuration
- `backend/main.py` - Configuration API
- `frontend/next.config.js` - Configuration Next.js
- `frontend/tailwind.config.js` - Configuration Tailwind

### Composants
- `frontend/components/ui/` - Composants de base
- `frontend/components/dashboard/` - Composants dashboard
- `frontend/components/charts/` - Composants charts

### API
- `backend/routers/strategies.py` - Routes stratégies
- `backend/routers/runs.py` - Routes runs
- `frontend/lib/api.ts` - Client API frontend

---

## 🚀 Workflow Typique

### 1. Démarrer les services
```powershell
# Terminal 1 - Backend
cd backend
python start.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 2. Utiliser l'application
1. Ouvrir `http://localhost:3000`
2. Naviguer vers `/run`
3. Sélectionner une stratégie
4. Lancer le backtest
5. Voir les résultats dans `/results/[runId]`
6. Comparer plusieurs runs dans `/compare`

### 3. Développement
- Modifier les fichiers
- Le hot-reload est actif (frontend et backend)
- Les changements sont visibles immédiatement

---

## 📚 Documentation Complète

- `GUIDE_MIGRATION.md` - Guide complet de migration
- `ETAPES_COMPLETEES.md` - Détail des étapes
- `RECAP_FINAL.md` - Récapitulatif final
- `frontend/README.md` - README frontend

---

## ✅ Checklist de Démarrage

- [ ] Backend démarré (`python start.py`)
- [ ] Backend accessible (`http://localhost:8000`)
- [ ] Node.js installé (`node --version`)
- [ ] Dépendances installées (`npm install`)
- [ ] Frontend démarré (`npm run dev`)
- [ ] Frontend accessible (`http://localhost:3000`)
- [ ] Tester une stratégie sur `/run`
- [ ] Voir les résultats sur `/results/[runId]`

---

**🎉 Tout est prêt ! Bon développement ! 🚀**
