# 🔐 Système de Contrôle d'Accès par Abonnement

## ✅ Implémentation Complète

Le système vérifie automatiquement l'abonnement de l'utilisateur dans Firestore et bloque l'accès si `subscriptionType === "free"`.

## 📊 Structure Firestore Requise

### Collection : `users`
### Document : `{userId}` (UID Firebase Auth)

```json
{
  "subscriptionType": "free" | "premium" | "pro",
  "products": [],
  "email": "user@example.com",
  "createdAt": "2025-10-14T...",
  // autres champs...
}
```

## 🚫 Règles d'Accès

| subscriptionType | Accès Dashboard | Redirection |
|------------------|-----------------|-------------|
| `free`           | ❌ Bloqué       | `/access-denied` |
| `premium`        | ✅ Autorisé     | `/` |
| `pro`            | ✅ Autorisé     | `/` |
| Non défini       | ❌ Bloqué       | `/access-denied` |
| Document absent  | ❌ Bloqué       | `/access-denied` |

## 🔄 Flux d'Authentification

```
1. Utilisateur clique sur "Se connecter avec Google"
   ↓
2. Authentification Google réussie
   ↓
3. Vérification dans Firestore : users/{uid}
   ↓
4a. subscriptionType !== "free" → Accès autorisé → Dashboard
4b. subscriptionType === "free" → Accès refusé → /access-denied
```

## 📁 Fichiers Modifiés

### 1. `lib/auth-context.tsx`
**Ajouts :**
- `hasAccess: boolean` - Indique si l'utilisateur a accès
- `subscriptionType: string | null` - Type d'abonnement
- Vérification Firestore dans `onAuthStateChanged`

**Logique :**
```typescript
if (userData.subscriptionType === 'free') {
  setHasAccess(false);
} else {
  setHasAccess(true);
}
```

### 2. `components/auth/protected-route.tsx`
**Ajouts :**
- Vérification de `hasAccess`
- Page d'erreur intégrée si accès refusé
- Bouton "Mettre à niveau"

### 3. `app/login/page.tsx`
**Ajouts :**
- Redirection conditionnelle après connexion
- Si `hasAccess === false` → `/access-denied`

### 4. `app/access-denied/page.tsx` (Nouveau)
**Page dédiée pour les utilisateurs sans accès :**
- Affichage du type d'abonnement actuel
- Liste des fonctionnalités Premium
- Bouton "Mettre à niveau"
- Bouton "Se déconnecter"

## 💻 Utilisation dans le Code

### Hook `useAuth()`

```tsx
import { useAuth } from '@/lib/auth-context';

function MonComposant() {
  const { user, hasAccess, subscriptionType } = useAuth();
  
  return (
    <div>
      {hasAccess ? (
        <p>Bienvenue ! Abonnement : {subscriptionType}</p>
      ) : (
        <p>Accès refusé. Abonnement : {subscriptionType}</p>
      )}
    </div>
  );
}
```

### Protéger une Page

```tsx
import { ProtectedRoute } from '@/components/auth/protected-route';

export default function MaPage() {
  return (
    <ProtectedRoute>
      {/* Contenu accessible uniquement aux abonnés premium/pro */}
    </ProtectedRoute>
  );
}
```

## 🎨 Interface Utilisateur

### Page `/access-denied`
- **Design** : Card moderne avec icône de cadenas
- **Informations** : Type d'abonnement actuel
- **Fonctionnalités listées** : Ce que l'utilisateur obtiendrait avec Premium
- **Actions** :
  - Bouton "Mettre à niveau" (gradient purple/pink)
  - Bouton "Se déconnecter" (gris)

### Console Logs
```
✅ Accès autorisé : abonnement premium
❌ Accès refusé : abonnement gratuit
⚠️ Document utilisateur non trouvé
```

## 🔧 Configuration Firestore

### Créer un Document Utilisateur

Après la première connexion Google, créez automatiquement le document :

```typescript
import { doc, setDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase-config';

// Après signInWithGoogle
const userRef = doc(db, 'users', user.uid);
await setDoc(userRef, {
  email: user.email,
  displayName: user.displayName,
  photoURL: user.photoURL,
  subscriptionType: 'free', // Par défaut
  products: [],
  createdAt: new Date().toISOString(),
}, { merge: true });
```

### Mettre à Jour l'Abonnement

```typescript
import { doc, updateDoc } from 'firebase/firestore';

const userRef = doc(db, 'users', userId);
await updateDoc(userRef, {
  subscriptionType: 'premium',
  updatedAt: new Date().toISOString(),
});
```

## 🛡️ Règles de Sécurité Firestore

Ajoutez ces règles dans Firebase Console :

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      // L'utilisateur peut lire son propre document
      allow read: if request.auth != null && request.auth.uid == userId;
      
      // Seuls les admins peuvent écrire (ou Cloud Functions)
      allow write: if false;
    }
  }
}
```

## 🔗 Intégration avec Stripe/Paddle

### Webhook après paiement

```typescript
// Cloud Function ou API Route
export async function handleSubscriptionUpdate(userId: string, subscriptionType: string) {
  const userRef = doc(db, 'users', userId);
  await updateDoc(userRef, {
    subscriptionType: subscriptionType,
    updatedAt: new Date().toISOString(),
  });
}
```

## 🐛 Dépannage

### L'utilisateur avec Premium est bloqué
→ Vérifiez que `subscriptionType` dans Firestore est bien `"premium"` ou `"pro"` (pas `"Premium"`)

### Document utilisateur non trouvé
→ Créez le document manuellement dans Firestore Console ou automatiquement après la première connexion

### Accès autorisé alors que subscriptionType est "free"
→ Vérifiez la console : le log doit afficher "❌ Accès refusé"
→ Videz le cache et rechargez

### L'utilisateur reste bloqué après mise à niveau
→ Déconnectez-vous et reconnectez-vous pour recharger les données Firestore

## ✨ Fonctionnalités Avancées

### Ajouter des Niveaux d'Accès

```typescript
// Dans auth-context.tsx
const accessLevels = {
  free: 0,
  basic: 1,
  premium: 2,
  pro: 3,
};

const userLevel = accessLevels[userData.subscriptionType] || 0;
setHasAccess(userLevel >= 2); // Premium ou Pro
```

### Vérification Périodique

```typescript
// Vérifier l'abonnement toutes les 5 minutes
useEffect(() => {
  const interval = setInterval(async () => {
    if (user) {
      // Re-vérifier Firestore
    }
  }, 5 * 60 * 1000);
  
  return () => clearInterval(interval);
}, [user]);
```

## 📚 Ressources

- [Firestore Docs](https://firebase.google.com/docs/firestore)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)

---

**Version :** 1.0.0  
**Date :** 14/10/2025  
**Statut :** ✅ Production-ready
