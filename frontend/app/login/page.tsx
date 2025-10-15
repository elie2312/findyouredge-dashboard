'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';
import Image from 'next/image';

export default function LoginPage() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signInWithGoogle, user, hasAccess, loading: authLoading } = useAuth();
  const router = useRouter();

  // Rediriger si déjà connecté
  useEffect(() => {
    if (!authLoading && user) {
      if (hasAccess) {
        router.push('/');
      } else {
        router.push('/access-denied');
      }
    }
  }, [user, hasAccess, authLoading, router]);

  const handleGoogleSignIn = async () => {
    setError('');
    setLoading(true);

    try {
      await signInWithGoogle();
      router.push('/');
    } catch (err: any) {
      console.error('Login error:', err);
      setError(
        err.code === 'auth/popup-closed-by-user'
          ? 'Connexion annulée'
          : err.code === 'auth/popup-blocked'
          ? 'Popup bloquée. Autorisez les popups pour ce site.'
          : err.code === 'auth/cancelled-popup-request'
          ? 'Connexion annulée'
          : 'Erreur de connexion. Veuillez réessayer.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center overflow-hidden relative p-4">
      {/* Même fond que la loading screen */}
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
          className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-brand-light/15 rounded-full blur-[120px]"
          animate={{ 
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.5, 0.3],
            x: [-30, 30, -30],
            y: [-20, 20, -20]
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-brand-lighter/15 rounded-full blur-[120px]"
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
        className="w-full max-w-2xl"
      >
        {/* Logo en gros */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 100, damping: 15 }}
            className="relative inline-block mb-6"
          >
            {/* Rotating glow ring */}
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background: 'conic-gradient(from 0deg, transparent 0%, rgba(123, 44, 191, 0.3) 25%, rgba(157, 78, 221, 0.4) 50%, rgba(199, 125, 255, 0.3) 75%, transparent 100%)',
                filter: 'blur(30px)',
                width: '400px',
                height: '400px',
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
              animate={{
                scale: [1, 1.02, 1],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <Image
                src="/logo_loading.png"
                alt="NQ Dashboard"
                width={300}
                height={300}
                className="relative z-10"
                priority
              />
            </motion.div>
          </motion.div>
          
          <motion.h1 
            className="text-4xl font-bold text-white mb-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            NQ Dashboard
          </motion.h1>
          <motion.p 
            className="text-gray-400 text-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            Connectez-vous pour accéder à votre dashboard de trading
          </motion.p>
        </div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7 }}
          className="bg-gray-800/30 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-purple-500/20"
        >
          <div className="space-y-6">
            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm"
              >
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span>{error}</span>
              </motion.div>
            )}

            {/* Google Sign In Button */}
            <button
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="w-full py-4 bg-white hover:bg-gray-100 disabled:bg-gray-300 disabled:cursor-not-allowed text-gray-900 font-semibold rounded-lg transition-all flex items-center justify-center gap-3 shadow-lg hover:shadow-xl"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-gray-400 border-t-gray-900 rounded-full animate-spin" />
                  <span>Connexion en cours...</span>
                </>
              ) : (
                <>
                  <svg className="w-6 h-6" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  <span>Se connecter avec Google</span>
                </>
              )}
            </button>

            {/* Info Text */}
            <p className="text-center text-gray-400 text-sm">
              Utilisez votre compte Google pour accéder au dashboard
            </p>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.p 
          className="text-center text-gray-500 text-sm mt-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          © 2025 NQ Dashboard. Tous droits réservés.
        </motion.p>
      </motion.div>
    </div>
  );
}
