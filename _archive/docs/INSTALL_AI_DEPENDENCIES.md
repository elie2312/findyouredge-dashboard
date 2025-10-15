# 📦 Installation des Dépendances pour le Chat IA

## Frontend - Installation des packages

Ouvrez un terminal dans le dossier `frontend` et exécutez :

```bash
cd frontend
npm install react-markdown@9.0.1
npm install react-syntax-highlighter@15.5.0
npm install @types/react-syntax-highlighter@15.5.11
```

Ou en une seule commande :

```bash
cd frontend
npm install react-markdown@9.0.1 react-syntax-highlighter@15.5.0 @types/react-syntax-highlighter@15.5.11
```

## Backend - Vérification

Le backend est déjà prêt, assurez-vous simplement que FastAPI est lancé :

```bash
cd backend
python main.py
```

## Lancement de l'application

1. **Backend** (Terminal 1) :
```bash
cd backend
python main.py
```

2. **Frontend** (Terminal 2) :
```bash
cd frontend
npm run dev
```

3. **Accès au Chat IA** :
   - Ouvrez votre navigateur sur : http://localhost:3000
   - Cliquez sur "IA Analyst" dans la barre de navigation

## 🚀 Fonctionnalités Disponibles

### Questions Prédéfinies
- "Analyse les performances du dernier backtest"
- "Montre la distribution des PnL par heure"
- "Analyse la volatilité sur les 30 derniers jours"
- "Génère un code pour calculer le Sharpe ratio"

### Commandes Avancées
- "Compare SuperTrend vs MA Cross"
- "Calcule le ratio de Calmar"
- "Analyse le drawdown maximal"
- "Montre les meilleures heures de trading"

## ⚠️ Troubleshooting

Si vous avez des erreurs TypeScript :
1. Supprimez `node_modules` et `package-lock.json`
2. Réinstallez tout : `npm install`
3. Redémarrez le serveur de développement

Si le backend ne répond pas :
1. Vérifiez que le port 8000 est libre
2. Vérifiez que FastAPI est bien lancé
3. Regardez les logs du backend pour les erreurs
