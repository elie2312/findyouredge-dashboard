# 🤖 Documentation Chat IA - Analyse de Données

## 📝 Vue d'ensemble

La nouvelle section **"Chat IA - Analyse de données"** est un assistant intelligent intégré à votre dashboard de trading. Il vous permet d'analyser vos données de backtest via une interface de chat conversationnelle.

## 🎯 Fonctionnalités Principales

### 1. Analyse de Performances
- Métriques détaillées de backtest (PnL, Win Rate, Drawdown)
- Calcul automatique du Sharpe Ratio
- Analyse de la distribution des gains/pertes

### 2. Analyse Quantitative
- Volatilité historique et actuelle
- Distribution temporelle des trades
- Identification des meilleures heures de trading
- Analyse du drawdown et temps de récupération

### 3. Génération de Code
- Scripts Python personnalisés
- Calcul des ratios (Sharpe, Calmar, Sortino)
- Frameworks d'analyse complets
- Code directement exécutable dans votre environnement

### 4. Comparaison de Stratégies
- Analyse comparative multi-stratégies
- Scoring normalisé
- Identification de la meilleure stratégie

## 🚀 Installation

### Méthode Automatique (Recommandée)
```powershell
# Exécutez le script PowerShell
.\install-ia-chat.ps1
```

### Méthode Manuelle
```bash
# Frontend
cd frontend
npm install react-markdown@9.0.1 react-syntax-highlighter@15.5.0 @types/react-syntax-highlighter@15.5.11

# Backend (déjà configuré)
cd ../backend
# Aucune installation supplémentaire requise
```

## 💬 Exemples de Questions

### Analyses de Base
- "Analyse les performances du dernier backtest"
- "Quelle est mon win rate actuel ?"
- "Montre-moi le PnL total"

### Analyses Temporelles
- "Montre la distribution des PnL par heure"
- "Quelles sont les meilleures heures pour trader ?"
- "Analyse l'activité de trading par période"

### Analyse de Risque
- "Calcule le drawdown maximal"
- "Quel est mon Sharpe ratio ?"
- "Analyse la volatilité des 30 derniers jours"

### Génération de Code
- "Génère un code pour calculer le Sharpe ratio"
- "Crée un script pour analyser le Calmar ratio"
- "Donne-moi un framework d'analyse complet"

### Comparaisons
- "Compare les performances de mes derniers backtests"
- "Quelle stratégie performe le mieux ?"
- "Analyse les différences entre deux périodes"

## 🔧 Architecture Technique

### Frontend (`/frontend/app/ia-analyst/page.tsx`)
- Interface React avec Framer Motion
- Markdown rendering avec syntax highlighting
- Communication temps réel avec le backend
- Cache intelligent des réponses

### Backend (`/backend/routers/ai_analyst.py`)
- API FastAPI avec endpoints REST
- Analyse des données de backtest
- Génération dynamique de code Python
- Accès direct aux fichiers CSV de résultats

### Hooks (`/frontend/hooks/useAIAnalyst.ts`)
- `useSendMessage`: Envoi de messages au chat
- `useAvailableRuns`: Récupération des backtests
- `useRunSummary`: Résumé détaillé d'un run

## 📊 Structure des Données

### Messages
```typescript
interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: {
    type?: 'chart' | 'table' | 'code' | 'analysis'
    data?: any
  }
}
```

### Context
```typescript
interface AnalysisContext {
  runId?: string
  strategy?: string
  dateRange?: { start: string; end: string }
  symbols?: string[]
}
```

## 🎨 Interface Utilisateur

### Zones Principales
1. **Header**: Titre et indicateurs de statut
2. **Zone de Chat**: Messages avec syntax highlighting
3. **Zone d'Input**: Saisie avec suggestions
4. **Actions Rapides**: Boutons pour questions fréquentes
5. **Sélecteur de Run**: Analyse de backtests spécifiques

### Design
- Theme violet/purple cohérent avec le dashboard
- Animations fluides avec Framer Motion
- Syntax highlighting pour le code
- Markdown rendering pour le formatage

## 🔍 Capacités d'Analyse

### Métriques Calculées
- **PnL Total**: Somme des profits/pertes
- **Win Rate**: Pourcentage de trades gagnants
- **Expectancy**: Gain moyen par trade
- **Max Drawdown**: Perte maximale depuis un pic
- **Sharpe Ratio**: Rendement ajusté au risque
- **Calmar Ratio**: Rendement / Max Drawdown
- **Sortino Ratio**: Pénalise uniquement la volatilité négative

### Sources de Données
- `trades.csv`: Historique des trades
- `picklog.csv`: Logs de sélection
- `config.json`: Configuration du backtest
- Données OHLCV: Prix historiques

## 🛡️ Gestion des Erreurs

### Fallback Intelligent
- Si le backend est indisponible, utilise des réponses mock
- Cache local des dernières analyses
- Reconnexion automatique

### Validation
- Vérification de l'existence des runs
- Validation des données avant analyse
- Messages d'erreur explicites

## 📈 Évolutions Futures

### Court Terme
- [ ] Export des analyses en PDF
- [ ] Graphiques interactifs intégrés
- [ ] Sauvegarde de l'historique de chat

### Moyen Terme
- [ ] Analyse prédictive avec ML
- [ ] Suggestions d'optimisation automatiques
- [ ] Comparaison multi-symboles

### Long Terme
- [ ] IA générative pour stratégies
- [ ] Backtesting direct depuis le chat
- [ ] Intégration avec des APIs externes

## 🤝 Support

### Problèmes Fréquents

**Les packages ne s'installent pas**
```bash
# Supprimez node_modules et réinstallez
rm -rf frontend/node_modules frontend/package-lock.json
cd frontend && npm install
```

**Le backend ne répond pas**
```bash
# Vérifiez que FastAPI est lancé
cd backend
python main.py
# Le serveur doit écouter sur http://localhost:8000
```

**Erreurs TypeScript**
```bash
# Installez les types manquants
cd frontend
npm install --save-dev @types/react-markdown
```

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Markdown](https://github.com/remarkjs/react-markdown)
- [Syntax Highlighter](https://github.com/react-syntax-highlighter/react-syntax-highlighter)
- [Framer Motion](https://www.framer.com/motion/)

---

**Version**: 1.0.0  
**Auteur**: Assistant IA  
**Date**: Octobre 2024  
**Licence**: MIT
