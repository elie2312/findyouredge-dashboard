'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import {
  User,
  signInWithPopup,
  GoogleAuthProvider,
  signOut as firebaseSignOut,
  onAuthStateChanged,
} from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';
import { auth, db } from './firebase-config';

interface UserSubscription {
  subscriptionType: 'free' | 'premium' | 'pro';
  products?: any[];
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  hasAccess: boolean;
  subscriptionType: string | null;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  hasAccess: false,
  subscriptionType: null,
  signInWithGoogle: async () => {},
  signOut: async () => {},
});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [hasAccess, setHasAccess] = useState(false);
  const [subscriptionType, setSubscriptionType] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setUser(user);
      
      if (user) {
        // Vérifier l'abonnement dans Firestore
        try {
          const userDocRef = doc(db, 'users', user.uid);
          const userDoc = await getDoc(userDocRef);
          
          if (userDoc.exists()) {
            const userData = userDoc.data() as UserSubscription;
            const subType = userData.subscriptionType || 'free';
            
            setSubscriptionType(subType);
            
            // Bloquer l'accès si subscriptionType est "free"
            if (subType === 'free') {
              setHasAccess(false);
              console.log('❌ Accès refusé : abonnement gratuit');
            } else {
              setHasAccess(true);
              console.log('✅ Accès autorisé : abonnement', subType);
            }
          } else {
            // Si le document n'existe pas, refuser l'accès par défaut
            console.log('⚠️ Document utilisateur non trouvé');
            setHasAccess(false);
            setSubscriptionType(null);
          }
        } catch (error) {
          console.error('Erreur lors de la vérification de l\'abonnement:', error);
          setHasAccess(false);
          setSubscriptionType(null);
        }
      } else {
        setHasAccess(false);
        setSubscriptionType(null);
      }
      
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const signInWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    await signInWithPopup(auth, provider);
  };

  const signOut = async () => {
    await firebaseSignOut(auth);
  };

  return (
    <AuthContext.Provider value={{ user, loading, hasAccess, subscriptionType, signInWithGoogle, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
