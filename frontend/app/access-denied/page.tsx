'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { motion } from 'framer-motion';
import { Lock, ArrowRight, LogOut, Shield } from 'lucide-react';

export default function AccessDeniedPage() {
  const { user, loading, hasAccess, subscriptionType, signOut } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Si l'utilisateur n'est pas connecté, rediriger vers login
    if (!loading && !user) {
      router.push('/login');
    }
    // Si l'utilisateur a accès, rediriger vers le dashboard
    if (!loading && hasAccess) {
      router.push('/');
    }
  }, [user, loading, hasAccess, router]);

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center overflow-hidden relative">
        <div className="absolute inset-0 -z-10">
          <motion.div 
            className="absolute inset-0 bg-gradient-to-br from-brand-dark/30 via-brand-darker/20 to-brand-base/30"
            animate={{ backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'] }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            style={{ backgroundSize: '200% 200%' }}
          />
        </div>
        <div className="w-16 h-16 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center overflow-hidden relative p-4">
      {/* Même fond que la loading screen et login */}
      <div className="absolute inset-0 -z-10">
        {/* Grille moderne avec effet de profondeur */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(to right, rgba(139, 92, 246, 0.1) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(139, 92, 246, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px',
          }}
        />
        
        {/* Grille secondaire plus fine */}
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `
              linear-gradient(to right, rgba(157, 78, 221, 0.15) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(157, 78, 221, 0.15) 1px, transparent 1px)
            `,
            backgroundSize: '20px 20px',
          }}
        />
        
        {/* Bougies stylisées en arrière-plan */}
        <svg className="absolute inset-0 w-full h-full opacity-10" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="candleGreen" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#00ff88" stopOpacity="0.6"/>
              <stop offset="100%" stopColor="#00ff88" stopOpacity="0.2"/>
            </linearGradient>
            <linearGradient id="candleRed" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ff4444" stopOpacity="0.6"/>
              <stop offset="100%" stopColor="#ff4444" stopOpacity="0.2"/>
            </linearGradient>
          </defs>
          
          {/* Bougies vertes (haussières) */}
          <rect x="10%" y="40%" width="3" height="80" fill="url(#candleGreen)" opacity="0.3"/>
          <rect x="10%" y="50%" width="12" height="50" fill="url(#candleGreen)" opacity="0.5"/>
          
          <rect x="25%" y="30%" width="3" height="100" fill="url(#candleGreen)" opacity="0.3"/>
          <rect x="25%" y="45%" width="12" height="60" fill="url(#candleGreen)" opacity="0.5"/>
          
          <rect x="55%" y="35%" width="3" height="90" fill="url(#candleGreen)" opacity="0.3"/>
          <rect x="55%" y="48%" width="12" height="55" fill="url(#candleGreen)" opacity="0.5"/>
          
          {/* Bougies rouges (baissières) */}
          <rect x="40%" y="45%" width="3" height="70" fill="url(#candleRed)" opacity="0.3"/>
          <rect x="40%" y="50%" width="12" height="45" fill="url(#candleRed)" opacity="0.5"/>
          
          <rect x="70%" y="50%" width="3" height="65" fill="url(#candleRed)" opacity="0.3"/>
          <rect x="70%" y="55%" width="12" height="40" fill="url(#candleRed)" opacity="0.5"/>
          
          <rect x="85%" y="42%" width="3" height="75" fill="url(#candleRed)" opacity="0.3"/>
          <rect x="85%" y="48%" width="12" height="48" fill="url(#candleRed)" opacity="0.5"/>
        </svg>
        
        {/* Gradient de base */}
        <motion.div 
          className="absolute inset-0 bg-gradient-to-br from-brand-dark/30 via-brand-darker/20 to-brand-base/30"
          animate={{ backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          style={{ backgroundSize: '200% 200%' }}
        />
        
        {/* Orbes lumineux animés */}
        <motion.div
          className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-red-500/10 rounded-full blur-[120px]"
          animate={{ 
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.5, 0.3],
            x: [-30, 30, -30],
            y: [-20, 20, -20]
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-orange-500/10 rounded-full blur-[120px]"
          animate={{ 
            scale: [1.3, 1, 1.3],
            opacity: [0.5, 0.3, 0.5],
            x: [30, -30, 30],
            y: [20, -20, 20]
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 2 }}
        />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl w-full"
      >
        {/* Icon avec animation */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 100, damping: 15 }}
            className="relative inline-block mb-6"
          >
            {/* Rotating glow ring - rouge/orange pour l'erreur */}
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background: 'conic-gradient(from 0deg, transparent 0%, rgba(239, 68, 68, 0.3) 25%, rgba(249, 115, 22, 0.4) 50%, rgba(251, 146, 60, 0.3) 75%, transparent 100%)',
                filter: 'blur(30px)',
                width: '200px',
                height: '200px',
                left: '50%',
                top: '50%',
                transform: 'translate(-50%, -50%)',
              }}
              animate={{
                rotate: 360,
              }}
              transition={{
                duration: 6,
                repeat: Infinity,
                ease: "linear"
              }}
            />
            
            <motion.div
              className="relative z-10 w-32 h-32 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-full flex items-center justify-center border-4 border-red-500/30"
              animate={{
                scale: [1, 1.05, 1],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <Lock className="w-16 h-16 text-red-400" />
            </motion.div>
          </motion.div>
          
          <motion.h1 
            className="text-4xl font-bold text-white mb-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            Accès Restreint
          </motion.h1>
          
          <motion.div 
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-full mb-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <Shield className="w-4 h-4 text-red-400" />
            <span className="text-sm text-gray-300">Abonnement actuel :</span>
            <span className="font-bold text-red-400 uppercase">{subscriptionType || 'Gratuit'}</span>
          </motion.div>
        </div>

        {/* Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7 }}
          className="bg-gray-800/30 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-red-500/20"
        >
          <div className="text-center mb-8">
            <p className="text-gray-300 text-lg">
              Vous devez disposer d'un abonnement <span className="font-semibold text-purple-400">Premium</span> ou <span className="font-semibold text-purple-400">Pro</span> pour accéder au dashboard.
            </p>
          </div>

          {/* Features List */}
          <div className="bg-gray-900/50 rounded-xl p-6 mb-6 border border-gray-700">
            <h3 className="text-white font-semibold mb-4">Avec un abonnement Premium :</h3>
            <ul className="space-y-3">
              {[
                'Accès complet au dashboard de trading',
                'Backtesting illimité de vos stratégies',
                'Analyse IA de vos performances',
                'Support prioritaire',
                'Mises à jour en temps réel'
              ].map((feature, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  className="flex items-center gap-3 text-gray-300"
                >
                  <div className="w-5 h-5 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-3 h-3 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span>{feature}</span>
                </motion.li>
              ))}
            </ul>
          </div>

          {/* Actions */}
          <div className="space-y-3">
            <button
              onClick={() => window.location.href = 'https://findyouredge.pro/login'}
              className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-lg transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 group"
            >
              <span>Mettre à niveau mon abonnement</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            
            <button
              onClick={handleSignOut}
              className="w-full py-3 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
            >
              <LogOut className="w-5 h-5" />
              <span>Se déconnecter</span>
            </button>
          </div>

          {/* Contact */}
          <motion.p 
            className="text-center text-gray-500 text-sm mt-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
          >
            Besoin d'aide ? <a href="mailto:support@example.com" className="text-purple-400 hover:text-purple-300 underline transition-colors">Contactez le support</a>
          </motion.p>
        </motion.div>
      </motion.div>
    </div>
  );
}
