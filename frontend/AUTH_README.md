# 🔐 Système d'Authentification Firebase

## 📁 Structure des fichiers

```
frontend/
├── lib/
│   ├── firebase-config.ts          # Configuration Firebase
│   └── auth-context.tsx            # Contexte React pour l'authentification
├── app/
│   ├── login/
│   │   └── page.tsx                # Page de connexion
│   └── layout.tsx                  # Layout principal (modifié)
├── components/
│   ├── auth/
│   │   └── protected-route.tsx     # Composant de protection des routes
│   └── dashboard/
│       └── header.tsx              # Header (modifié avec déconnexion)
├── middleware.ts                   # Middleware Next.js
├── .env.local                      # Variables d'environnement (à créer)
└── .env.local.example              # Exemple de configuration
```

## 🚀 Installation rapide

### Option 1 : Script automatique (Recommandé)
```powershell
cd frontend
.\setup-firebase.ps1
```

### Option 2 : Installation manuelle
```bash
cd frontend
npm install firebase
cp .env.local.example .env.local
# Puis éditez .env.local avec vos credentials
```

## 🔑 Configuration Firebase

### 1. Récupérer les credentials

1. Allez sur [Firebase Console](https://console.firebase.google.com/)
2. Sélectionnez votre projet
3. **⚙️ Paramètres** → **Paramètres du projet** → **Général**
4. Descendez jusqu'à **Vos applications**
5. Copiez les valeurs de configuration

### 2. Remplir `.env.local`

```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIza...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=votre-projet.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=votre-projet
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=votre-projet.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abc123
```

### 3. Activer l'authentification

1. **Authentication** → **Get started**
2. **Sign-in method** → **Email/Password** → **Activer**
3. **Users** → **Add user** → Créer un compte de test

## 💻 Utilisation

### Hook `useAuth()`

Utilisez ce hook dans n'importe quel composant :

```tsx
import { useAuth } from '@/lib/auth-context';

function MonComposant() {
  const { user, loading, signIn, signOut } = useAuth();
  
  if (loading) return <div>Chargement...</div>;
  
  return (
    <div>
      {user ? (
        <>
          <p>Connecté en tant que {user.email}</p>
          <button onClick={signOut}>Déconnexion</button>
        </>
      ) : (
        <p>Non connecté</p>
      )}
    </div>
  );
}
```

### Protéger une page

Enveloppez votre page avec `ProtectedRoute` :

```tsx
import { ProtectedRoute } from '@/components/auth/protected-route';

export default function MaPageProtegee() {
  return (
    <ProtectedRoute>
      <div>Contenu accessible uniquement aux utilisateurs connectés</div>
    </ProtectedRoute>
  );
}
```

### Connexion programmatique

```tsx
const { signIn } = useAuth();

try {
  await signIn('user@example.com', 'password123');
  router.push('/dashboard');
} catch (error) {
  console.error('Erreur de connexion:', error);
}
```

## 🎨 Interface utilisateur

### Page de login (`/login`)
- Design moderne avec animations Framer Motion
- Validation des champs
- Messages d'erreur clairs
- Redirection automatique si déjà connecté

### Header
- **Badge utilisateur** : Affiche l'email de l'utilisateur connecté
- **Bouton de déconnexion** : Badge rouge avec icône LogOut
- **Responsive** : S'adapte aux mobiles

## 🛡️ Sécurité

### Côté client
- ✅ Contexte React pour gérer l'état d'authentification
- ✅ Redirection automatique vers `/login` si non connecté
- ✅ Protection des routes avec `ProtectedRoute`

### Côté serveur (à implémenter)
Pour une sécurité renforcée, vous devriez :
1. Utiliser des tokens JWT
2. Les stocker dans des cookies HTTP-only
3. Les vérifier dans le middleware Next.js

## 📊 API disponible

### `useAuth()` Hook

```typescript
interface AuthContextType {
  user: User | null;              // Utilisateur Firebase ou null
  loading: boolean;               // État de chargement
  signIn: (email, password) => Promise<void>;
  signUp: (email, password) => Promise<void>;
  signOut: () => Promise<void>;
}
```

### Objet `user` (Firebase)

```typescript
{
  uid: string;                    // ID unique de l'utilisateur
  email: string | null;           // Email
  emailVerified: boolean;         // Email vérifié ?
  displayName: string | null;     // Nom d'affichage
  photoURL: string | null;        // URL de la photo
  // ... autres propriétés Firebase
}
```

## 🔧 Personnalisation

### Changer le logo de la page de login

Modifiez `app/login/page.tsx` :

```tsx
<img src="/votre-logo.png" alt="Logo" className="h-16 w-auto" />
```

### Ajouter l'inscription

Le hook `signUp()` est déjà disponible :

```tsx
const { signUp } = useAuth();

await signUp('newuser@example.com', 'password123');
```

### Ajouter la récupération de mot de passe

```tsx
import { sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '@/lib/firebase-config';

await sendPasswordResetEmail(auth, email);
```

## 🐛 Dépannage

### Erreur : "Firebase: Error (auth/invalid-api-key)"
→ Vérifiez `NEXT_PUBLIC_FIREBASE_API_KEY` dans `.env.local`

### Erreur : "Firebase: Error (auth/invalid-credential)"
→ Email ou mot de passe incorrect

### Le bouton de déconnexion n'apparaît pas
→ Vérifiez que vous êtes connecté et que le header utilise `useAuth()`

### Erreur : "Cannot find module '@/lib/auth-context'"
→ Redémarrez le serveur de développement (`npm run dev`)

### Les variables d'environnement ne sont pas chargées
→ Redémarrez le serveur après avoir modifié `.env.local`

## 📚 Ressources

- [Firebase Authentication Docs](https://firebase.google.com/docs/auth)
- [Next.js Authentication](https://nextjs.org/docs/authentication)
- [React Context API](https://react.dev/reference/react/useContext)

## ✨ Fonctionnalités futures

- [ ] Inscription de nouveaux utilisateurs
- [ ] Récupération de mot de passe
- [ ] Authentification Google
- [ ] Authentification GitHub
- [ ] Vérification d'email
- [ ] Profil utilisateur dans Firestore
- [ ] Rôles et permissions
- [ ] Protection serveur avec JWT

---

**Version :** 1.0.0  
**Date :** 14/10/2025  
**Statut :** ✅ Production-ready
