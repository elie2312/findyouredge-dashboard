'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { motion } from 'framer-motion';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading, hasAccess, subscriptionType } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  // Afficher un loader pendant la vérification
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="text-center"
        >
          <div className="w-16 h-16 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400 text-sm">Vérification de l'authentification...</p>
        </motion.div>
      </div>
    );
  }

  // Si pas d'utilisateur, ne rien afficher (redirection en cours)
  if (!user) {
    return null;
  }

  // Si l'utilisateur n'a pas accès (abonnement gratuit)
  if (!hasAccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md w-full"
        >
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-red-500/30 text-center">
            <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            
            <h1 className="text-2xl font-bold text-white mb-3">Accès Restreint</h1>
            <p className="text-gray-300 mb-2">
              Votre abonnement actuel : <span className="font-semibold text-red-400">{subscriptionType || 'Gratuit'}</span>
            </p>
            <p className="text-gray-400 mb-6">
              Vous devez disposer d'un abonnement premium pour accéder au dashboard.
            </p>
            
            <div className="space-y-3">
              <button
                onClick={() => window.location.href = 'https://votre-site-abonnement.com'}
                className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-lg transition-all shadow-lg"
              >
                Mettre à niveau mon abonnement
              </button>
              
              <button
                onClick={() => {
                  router.push('/login');
                  window.location.reload();
                }}
                className="w-full py-3 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition-all"
              >
                Se déconnecter
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  // Utilisateur authentifié avec accès, afficher le contenu
  return <>{children}</>;
}
