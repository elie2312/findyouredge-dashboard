# 🔐 Configuration Authentification Google

## ✅ Modifications effectuées

Le système d'authentification a été **converti pour utiliser uniquement Google Sign-In** :

- ✅ `lib/auth-context.tsx` - Modifié pour Google Auth
- ✅ `app/login/page.tsx` - Bouton "Se connecter avec Google"
- ✅ Suppression des champs email/password

## 🚀 Configuration en 3 étapes

### Étape 1 : Créer le fichier `.env.local`

Créez le fichier `frontend/.env.local` avec ce contenu :

```env
# Firebase Configuration - NQ Dashboard
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyDTU1G5GclNJQQmaEtQjUuJIpSyWZIgtKA
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=edge-algo.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=edge-algo
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=edge-algo.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=1057898209015
NEXT_PUBLIC_FIREBASE_APP_ID=1:1057898209015:web:ecf5ff6d38b4b1ed123df2
```

**Commande PowerShell pour créer le fichier :**
```powershell
cd frontend
@"
# Firebase Configuration - NQ Dashboard
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyDTU1G5GclNJQQmaEtQjUuJIpSyWZIgtKA
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=edge-algo.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=edge-algo
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=edge-algo.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=1057898209015
NEXT_PUBLIC_FIREBASE_APP_ID=1:1057898209015:web:ecf5ff6d38b4b1ed123df2
"@ | Out-File -FilePath ".env.local" -Encoding utf8
```

### Étape 2 : Activer Google Sign-In dans Firebase

1. Allez sur https://console.firebase.google.com/project/edge-algo
2. **Authentication** → **Get started** (si pas déjà fait)
3. **Sign-in method** → **Google** → **Activer**
4. Choisissez un email de support (votre email)
5. **Enregistrer**

### Étape 3 : Installer Firebase et démarrer

```bash
cd frontend
npm install firebase
npm run dev
```

## 🎯 Tester la connexion

1. Accédez à http://localhost:3000/login
2. Cliquez sur **"Se connecter avec Google"**
3. Sélectionnez votre compte Google
4. Vous serez redirigé vers le dashboard

## 🎨 Interface utilisateur

### Page de login
- ✅ Bouton blanc avec logo Google officiel
- ✅ Design moderne et épuré
- ✅ Animations fluides
- ✅ Messages d'erreur clairs

### Header
- ✅ Badge utilisateur avec email Google
- ✅ Photo de profil Google (si disponible)
- ✅ Bouton de déconnexion

## 🔧 Configuration Firebase Console

### Domaines autorisés

Si vous déployez en production, ajoutez vos domaines :
1. Firebase Console → **Authentication** → **Settings**
2. **Authorized domains** → **Add domain**
3. Ajoutez votre domaine de production

### Personnalisation

Dans Firebase Console → **Authentication** → **Settings** → **User actions** :
- Personnalisez l'email de support
- Configurez le nom de l'application

## 💻 Utilisation dans le code

### Hook `useAuth()`

```tsx
import { useAuth } from '@/lib/auth-context';

function MonComposant() {
  const { user, loading, signInWithGoogle, signOut } = useAuth();
  
  if (loading) return <div>Chargement...</div>;
  
  return (
    <div>
      {user ? (
        <>
          <p>Connecté : {user.email}</p>
          <img src={user.photoURL} alt="Avatar" />
          <button onClick={signOut}>Déconnexion</button>
        </>
      ) : (
        <button onClick={signInWithGoogle}>
          Se connecter avec Google
        </button>
      )}
    </div>
  );
}
```

### Données utilisateur disponibles

```typescript
user.uid              // ID unique
user.email            // Email Google
user.displayName      // Nom complet
user.photoURL         // URL de la photo de profil
user.emailVerified    // true (Google vérifie automatiquement)
```

## 🛡️ Sécurité

### Avantages de Google Sign-In
- ✅ Pas de gestion de mots de passe
- ✅ Authentification à deux facteurs de Google
- ✅ Emails automatiquement vérifiés
- ✅ Sécurité gérée par Google

### Protection des routes

Le composant `ProtectedRoute` fonctionne toujours :

```tsx
import { ProtectedRoute } from '@/components/auth/protected-route';

export default function MaPage() {
  return (
    <ProtectedRoute>
      <div>Contenu protégé</div>
    </ProtectedRoute>
  );
}
```

## 🐛 Dépannage

### Erreur : "Popup bloquée"
→ Autorisez les popups pour localhost:3000 dans votre navigateur

### Erreur : "auth/unauthorized-domain"
→ Ajoutez votre domaine dans Firebase Console → Authentication → Settings → Authorized domains

### Erreur : "auth/operation-not-allowed"
→ Activez Google Sign-In dans Firebase Console → Authentication → Sign-in method

### Le bouton ne fait rien
→ Vérifiez que le fichier `.env.local` existe et contient les bonnes valeurs
→ Redémarrez le serveur après avoir créé `.env.local`

## ✨ Fonctionnalités

### Implémentées
- ✅ Connexion avec Google
- ✅ Déconnexion
- ✅ Gestion de session automatique
- ✅ Redirection automatique
- ✅ Protection des routes
- ✅ Affichage de la photo de profil

### Possibles extensions
- [ ] Restriction par domaine email (@votreentreprise.com)
- [ ] Stockage de données utilisateur dans Firestore
- [ ] Rôles et permissions
- [ ] Logs de connexion

## 📚 Ressources

- [Google Sign-In Docs](https://firebase.google.com/docs/auth/web/google-signin)
- [Firebase Console](https://console.firebase.google.com/project/edge-algo)
- [Popup vs Redirect](https://firebase.google.com/docs/auth/web/google-signin#choose_an_authentication_flow)

---

**Version :** 2.0.0 (Google Auth)  
**Date :** 14/10/2025  
**Statut :** ✅ Prêt à l'emploi
