# 🔥 Configuration Firebase - Guide d'installation

## ✅ Fichiers créés

Tous les fichiers nécessaires ont été créés :

- ✅ `lib/firebase-config.ts` - Configuration Firebase
- ✅ `lib/auth-context.tsx` - Contexte d'authentification React
- ✅ `app/login/page.tsx` - Page de connexion
- ✅ `components/auth/protected-route.tsx` - Composant de protection des routes
- ✅ `middleware.ts` - Middleware Next.js
- ✅ `app/layout.tsx` - Modifié pour intégrer AuthProvider
- ✅ `components/dashboard/header.tsx` - Modifié avec bouton de déconnexion

## 📦 Étape 1 : Installation de Firebase

Exécutez cette commande dans le dossier `frontend` :

```bash
npm install firebase
```

## 🔑 Étape 2 : Configuration des variables d'environnement

### 2.1 Récupérer vos credentials Firebase

1. Allez sur [Firebase Console](https://console.firebase.google.com/)
2. Sélectionnez votre projet existant
3. Cliquez sur l'icône **⚙️ Paramètres** → **Paramètres du projet**
4. Dans l'onglet **Général**, descendez jusqu'à **Vos applications**
5. Si vous n'avez pas encore d'application web, cliquez sur **</>** (Web) pour en créer une
6. Copiez les valeurs de configuration

### 2.2 Créer le fichier `.env.local`

Créez un fichier `.env.local` à la racine du dossier `frontend` avec ce contenu :

```env
NEXT_PUBLIC_FIREBASE_API_KEY=votre_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=votre_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=votre_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=votre_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=votre_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=votre_app_id
```

**⚠️ Important :** Remplacez les valeurs par vos vraies credentials Firebase !

### 2.3 Vérifier que `.env.local` est dans `.gitignore`

Le fichier `.env.local` ne doit **JAMAIS** être commité dans Git. Vérifiez qu'il est bien dans `.gitignore`.

## 🔐 Étape 3 : Activer l'authentification dans Firebase

1. Dans Firebase Console, allez dans **Authentication** (menu de gauche)
2. Cliquez sur **Get started** si ce n'est pas déjà fait
3. Dans l'onglet **Sign-in method**, activez **Email/Password**
4. Créez un utilisateur de test :
   - Allez dans l'onglet **Users**
   - Cliquez sur **Add user**
   - Entrez un email et un mot de passe

## 🚀 Étape 4 : Tester l'authentification

1. **Démarrer le serveur de développement :**
   ```bash
   npm run dev
   ```

2. **Accéder à la page de login :**
   ```
   http://localhost:3000/login
   ```

3. **Se connecter avec l'utilisateur de test**

4. **Vérifier que :**
   - ✅ La connexion fonctionne
   - ✅ Vous êtes redirigé vers la page d'accueil
   - ✅ Votre email s'affiche dans le header
   - ✅ Le bouton "Déconnexion" est visible
   - ✅ La déconnexion vous ramène à `/login`

## 🛡️ Étape 5 : Protéger les routes (optionnel)

Si vous voulez forcer la connexion pour accéder aux pages, vous pouvez utiliser le composant `ProtectedRoute`.

### Exemple : Protéger la page d'accueil

Modifiez `app/page.tsx` :

```tsx
import { ProtectedRoute } from '@/components/auth/protected-route';

export default function HomePage() {
  return (
    <ProtectedRoute>
      {/* Votre contenu existant */}
    </ProtectedRoute>
  );
}
```

### Protéger toutes les pages sauf `/login`

Le middleware est déjà configuré, mais pour une vraie protection serveur, vous devriez :
1. Utiliser des tokens JWT
2. Les stocker dans des cookies HTTP-only
3. Les vérifier dans le middleware

Pour l'instant, la protection se fait côté client avec `AuthProvider`.

## 📱 Fonctionnalités disponibles

### Dans le Header
- **Email de l'utilisateur** : Affiché dans une badge violet
- **Bouton de déconnexion** : Badge rouge avec icône LogOut

### Page de Login
- **Design moderne** : Animations Framer Motion
- **Validation** : Messages d'erreur clairs
- **Auto-complétion** : Support des gestionnaires de mots de passe
- **Redirection automatique** : Si déjà connecté

### Contexte d'authentification
Utilisez le hook `useAuth()` dans n'importe quel composant :

```tsx
import { useAuth } from '@/lib/auth-context';

function MonComposant() {
  const { user, loading, signIn, signOut } = useAuth();
  
  if (loading) return <div>Chargement...</div>;
  if (!user) return <div>Non connecté</div>;
  
  return <div>Bonjour {user.email}</div>;
}
```

## 🔧 Dépannage

### Erreur : "Firebase: Error (auth/invalid-api-key)"
→ Vérifiez que votre `NEXT_PUBLIC_FIREBASE_API_KEY` est correct dans `.env.local`

### Erreur : "Firebase: Error (auth/invalid-credential)"
→ Email ou mot de passe incorrect. Vérifiez dans Firebase Console > Authentication > Users

### Le bouton de déconnexion n'apparaît pas
→ Vérifiez que vous êtes bien connecté et que le composant Header utilise `useAuth()`

### Redirection infinie
→ Vérifiez que la page `/login` n'utilise pas `ProtectedRoute`

## 📚 Documentation

- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)
- [React Context](https://react.dev/reference/react/useContext)

## ✨ Prochaines étapes

- [ ] Ajouter la récupération de mot de passe
- [ ] Ajouter l'inscription de nouveaux utilisateurs
- [ ] Implémenter des tokens JWT pour la protection serveur
- [ ] Ajouter l'authentification Google/GitHub
- [ ] Stocker des données utilisateur dans Firestore

---

**Créé le :** 14/10/2025  
**Statut :** ✅ Prêt à l'emploi
