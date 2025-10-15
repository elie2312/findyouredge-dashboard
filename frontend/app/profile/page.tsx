'use client';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { useAuth } from '@/lib/auth-context';
import { Header } from '@/components/dashboard/header';
import { Footer } from '@/components/dashboard/footer';
import { motion } from 'framer-motion';
import { User, Mail, Calendar, Shield } from 'lucide-react';

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  );
}

function ProfileContent() {
  const { user } = useAuth();

  if (!user) return null;

  const createdAt = user.metadata.creationTime 
    ? new Date(user.metadata.creationTime).toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    : 'Inconnue';

  const lastSignIn = user.metadata.lastSignInTime
    ? new Date(user.metadata.lastSignInTime).toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    : 'Inconnue';

  return (
    <>
      <Header />
      <main className="flex-1 px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Page Title */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-4xl font-bold text-white mb-2">Mon Profil</h1>
            <p className="text-gray-400">Informations de votre compte</p>
          </motion.div>

          {/* Profile Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gray-800/50 backdrop-blur-lg border border-violet-400/30 rounded-2xl p-8 shadow-lg"
          >
            {/* Avatar & Name */}
            <div className="flex items-center gap-6 mb-8 pb-8 border-b border-gray-700">
              <div className="w-20 h-20 bg-gradient-to-br from-violet-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="w-10 h-10 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">
                  {user.displayName || 'Utilisateur'}
                </h2>
                <p className="text-gray-400">{user.email}</p>
              </div>
            </div>

            {/* Info Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Email */}
              <div className="flex items-start gap-4 p-4 bg-gray-900/50 rounded-xl border border-gray-700">
                <div className="w-10 h-10 bg-violet-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Mail className="w-5 h-5 text-violet-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Email</p>
                  <p className="text-white font-medium">{user.email}</p>
                  {user.emailVerified ? (
                    <span className="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                      <Shield className="w-3 h-3" />
                      Vérifié
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-orange-500/20 text-orange-400 text-xs rounded-full">
                      Non vérifié
                    </span>
                  )}
                </div>
              </div>

              {/* User ID */}
              <div className="flex items-start gap-4 p-4 bg-gray-900/50 rounded-xl border border-gray-700">
                <div className="w-10 h-10 bg-violet-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Shield className="w-5 h-5 text-violet-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">ID Utilisateur</p>
                  <p className="text-white font-mono text-sm break-all">{user.uid}</p>
                </div>
              </div>

              {/* Creation Date */}
              <div className="flex items-start gap-4 p-4 bg-gray-900/50 rounded-xl border border-gray-700">
                <div className="w-10 h-10 bg-violet-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Calendar className="w-5 h-5 text-violet-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Compte créé le</p>
                  <p className="text-white font-medium">{createdAt}</p>
                </div>
              </div>

              {/* Last Sign In */}
              <div className="flex items-start gap-4 p-4 bg-gray-900/50 rounded-xl border border-gray-700">
                <div className="w-10 h-10 bg-violet-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Calendar className="w-5 h-5 text-violet-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Dernière connexion</p>
                  <p className="text-white font-medium">{lastSignIn}</p>
                </div>
              </div>
            </div>

            {/* Provider Info */}
            <div className="mt-8 pt-8 border-t border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Méthode d'authentification</h3>
              <div className="flex flex-wrap gap-2">
                {user.providerData.map((provider, index) => (
                  <span
                    key={index}
                    className="px-3 py-1.5 bg-violet-500/20 text-violet-300 text-sm rounded-full border border-violet-400/30"
                  >
                    {provider.providerId === 'password' ? 'Email/Password' : provider.providerId}
                  </span>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Info Box */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mt-6 p-4 bg-blue-500/10 border border-blue-400/30 rounded-xl"
          >
            <p className="text-blue-300 text-sm">
              💡 <strong>Astuce :</strong> Cette page est protégée par le composant <code className="px-1 py-0.5 bg-blue-500/20 rounded">ProtectedRoute</code>. 
              Seuls les utilisateurs connectés peuvent y accéder.
            </p>
          </motion.div>
        </div>
      </main>
      <Footer />
    </>
  );
}
