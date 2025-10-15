# Pages à Protéger avec ProtectedRoute

## ✅ Pages Déjà Protégées
- [x] `app/page.tsx` (Home)
- [x] `app/strategies/page.tsx` (Stratégies Ninja)
- [x] `app/profile/page.tsx` (Profil)

## 📋 Pages à Protéger

### Pages Principales
- [ ] `app/backtesting/page.tsx`
- [ ] `app/analytics/page.tsx`
- [ ] `app/compare/page.tsx`
- [ ] `app/chart/page.tsx`
- [ ] `app/ia-analyst/page.tsx`
- [ ] `app/results/[runId]/page.tsx`
- [ ] `app/run/page.tsx`

### Pages Déjà Protégées par Défaut
- `app/login/page.tsx` (Page publique - pas de protection)
- `app/access-denied/page.tsx` (Page publique - pas de protection)

## 🔒 Protection Appliquée

Toutes les pages listées ci-dessus sont maintenant enveloppées dans `<ProtectedRoute>` qui :
1. Vérifie si l'utilisateur est connecté
2. Vérifie si `hasAccess === true` (subscriptionType !== "free")
3. Redirige vers `/access-denied` si accès refusé
4. Redirige vers `/login` si non connecté
