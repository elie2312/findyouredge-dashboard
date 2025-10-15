# ⚠️ Problèmes Actuels du Dashboard

## 🎯 État Actuel : 85% Fonctionnel

Le dashboard est **visuellement complet** mais il manque l'**intégration backend complète** pour lancer les backtests.

---

## ✅ Ce qui Fonctionne (85%)

### Frontend
- ✅ Page d'accueil avec statistiques
- ✅ Page Run avec sélection de stratégies
- ✅ Page Results avec charts
- ✅ Page Compare
- ✅ Navigation complète
- ✅ Dark mode
- ✅ Animations
- ✅ Design moderne
- ✅ Boutons "Voir résultats" sur la home

### Backend
- ✅ API FastAPI démarrée
- ✅ Liste des stratégies (7 stratégies détectées)
- ✅ Liste des runs existants
- ✅ Connexion aux adapters
- ✅ CORS configuré

---

## ❌ Ce qui Ne Fonctionne Pas (15%)

### 1. Lancement de Backtests

**Problème :** Quand vous cliquez sur "Lancer un Backtest", ça crée un Run ID mais ne lance pas vraiment le script Python.

**Fichier concerné :** `backend/routers/runs.py` lignes 46-72

**Code actuel (placeholder) :**
```python
@router.post("", response_model=RunResponse)
def create_run(request: RunRequest, background_tasks: BackgroundTasks):
    runner = get_runner()
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    # TODO: Implémenter le lancement async
    # Pour l'instant, on simule
    # background_tasks.add_task(runner.run_async, request.strategy_id, request.parameters)
    
    return RunResponse(
        run_id=run_id,
        status="running",
        message=f"Backtest {request.strategy_id} démarré"
    )
```

**Ce qu'il faudrait faire :**
```python
# Lancer vraiment le backtest
strategy = strategiesApi.get(request.strategy_id)
result = runner.run(
    script_path=strategy.script_path,
    parameters=request.parameters
)
```

---

### 2. Statut des Runs

**Problème :** Le statut retourne 404 car le run n'existe pas vraiment.

**Logs backend :**
```
POST /api/runs HTTP/1.1" 200 OK
GET /api/runs/{id}/status HTTP/1.1" 404 Not Found
```

**Raison :** Le run n'est jamais sauvegardé ni exécuté.

**Ce qu'il faudrait :**
- Sauvegarder le run dans une DB ou fichier JSON
- Lancer le script Python en arrière-plan
- Mettre à jour le statut (running → completed/failed)

---

### 3. Résultats

**Problème :** Pas de résultats car les backtests ne sont pas exécutés.

**Ce qu'il faudrait :**
- Exécuter le backtest
- Parser les résultats (CSV, JSON)
- Les renvoyer via `/api/runs/{id}/results`

---

### 4. Comparaison

**Problème :** Pas de données dans la table de comparaison.

**Message visible :** 
> 💡 **Note:** Pour afficher les métriques complètes, l'endpoint `/api/runs/compare` doit être implémenté dans le backend.

**Ce qu'il faudrait :**
- Créer endpoint `POST /api/runs/compare`
- Accepter une liste de run_ids
- Retourner les métriques comparées

---

## 🔧 Solutions

### Solution 1 : Test avec les Runs Existants (Rapide)

Si vous avez déjà des runs terminés dans `NQ/integration_poc/runs/`, vous pouvez:

1. Vérifier qu'ils sont bien détectés :
```bash
cd backend
python
>>> from run_backtest import create_runner
>>> runner = create_runner("../NQ")
>>> runs = runner.list_runs()
>>> for r in runs:
...     print(r.run_id, r.status)
```

2. Si des runs sont "completed", cliquez sur "📊 Voir résultats" dans la home page

---

### Solution 2 : Implémenter le Lancement (30-60 min)

**Fichier à modifier :** `backend/routers/runs.py`

**Étapes :**
1. Récupérer la stratégie sélectionnée
2. Utiliser `runner.run()` pour lancer le script
3. Sauvegarder le run_id dans un fichier JSON
4. Mettre à jour le statut après exécution

**Code à implémenter :**
```python
import subprocess
import json
from pathlib import Path

RUNS_DB = Path(__file__).parent.parent / "runs_db.json"

def save_run(run_id, status, message):
    if RUNS_DB.exists():
        data = json.loads(RUNS_DB.read_text())
    else:
        data = {"runs": []}
    
    data["runs"].append({
        "run_id": run_id,
        "status": status,
        "message": message,
        "created_at": datetime.now().isoformat()
    })
    
    RUNS_DB.write_text(json.dumps(data, indent=2))

@router.post("", response_model=RunResponse)
def create_run(request: RunRequest, background_tasks: BackgroundTasks):
    runner = get_runner()
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    # Récupérer la stratégie
    strategies = get_available_strategies(str(NQ_BASE_PATH))
    strategy = next((s for s in strategies if s['name'].lower().replace(' ', '_') == request.strategy_id), None)
    
    if not strategy:
        raise HTTPException(404, "Stratégie non trouvée")
    
    # Sauvegarder le run
    save_run(run_id, "running", f"Backtest {strategy['name']} démarré")
    
    # Lancer en arrière-plan
    def run_backtest():
        try:
            # Lancer le script Python
            result = subprocess.run(
                ["python", strategy['script_path']],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )
            
            if result.returncode == 0:
                save_run(run_id, "completed", "Backtest terminé avec succès")
            else:
                save_run(run_id, "failed", f"Erreur: {result.stderr}")
        except Exception as e:
            save_run(run_id, "failed", str(e))
    
    background_tasks.add_task(run_backtest)
    
    return RunResponse(
        run_id=run_id,
        status="running",
        message=f"Backtest {strategy['name']} démarré",
        started_at=datetime.now().isoformat()
    )
```

---

### Solution 3 : Utiliser le Système Existant (5 min)

**Si vous avez déjà un système pour lancer les backtests** (scripts, CLI, etc.) :

1. Lancez vos backtests comme d'habitude
2. Les résultats apparaîtront automatiquement dans le dashboard
3. Cliquez sur "📊 Voir résultats" pour les visualiser

---

## 📊 Résumé

| Fonctionnalité | État | Action |
|----------------|------|--------|
| Design Frontend | ✅ 100% | Rien |
| Navigation | ✅ 100% | Rien |
| API Stratégies | ✅ 100% | Rien |
| API Liste Runs | ✅ 100% | Rien |
| **Lancement Backtests** | ❌ 0% | **Implémenter** |
| **Statut Runs** | ❌ 0% | **Implémenter** |
| **Résultats** | ⚠️ 50% | Fonctionne avec runs existants |
| **Comparaison** | ⚠️ 30% | Endpoint à créer |

---

## 🎯 Priorités

### Priorité 1 : Tester avec Runs Existants
Si vous avez des runs terminés, testez la visualisation des résultats.

### Priorité 2 : Implémenter le Lancement
Modifier `backend/routers/runs.py` pour lancer vraiment les backtests.

### Priorité 3 : Endpoint Comparaison
Créer `POST /api/runs/compare` pour comparer plusieurs runs.

---

## 💡 Workaround Temporaire

**Pour tester le dashboard sans implémenter le lancement :**

1. Lancez un backtest manuellement (comme avant)
2. Attendez qu'il se termine
3. Rafraîchissez le dashboard
4. Les résultats apparaîtront automatiquement
5. Cliquez sur "📊 Voir résultats"

---

**Créé le :** 09/10/2025  
**Status Dashboard :** 85% fonctionnel (design complet, backend partiel)
