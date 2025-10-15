'use client'

import { motion } from 'framer-motion'
import Image from 'next/image'

interface LoadingScreenProps {
  onComplete?: () => void
}

export function LoadingScreen({ onComplete }: LoadingScreenProps) {
  return (
    <motion.div 
      className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden"
      exit={{ 
        scale: 0.95,
        y: -200,
        height: '600px',
        borderRadius: '24px',
        opacity: 0,
        transition: { duration: 0.8, ease: [0.43, 0.13, 0.23, 0.96], delay: 0.3 }
      }}
    >
      {/* Même fond que la hero section */}
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

      {/* Logo container */}
      <motion.div 
        className="relative z-10 flex flex-col items-center"
        exit={{
          opacity: 0,
          scale: 0.8,
          transition: { duration: 0.3, ease: "easeOut" }
        }}
      >
        {/* Rotating glow ring - effet plus doux */}
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            background: 'conic-gradient(from 0deg, transparent 0%, rgba(123, 44, 191, 0.3) 25%, rgba(157, 78, 221, 0.4) 50%, rgba(199, 125, 255, 0.3) 75%, transparent 100%)',
            filter: 'blur(30px)',
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

        {/* Logo with subtle pulse animation */}
        <motion.div
          className="relative z-10"
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
            alt="Loading"
            width={350}
            height={350}
            className="relative z-10"
            priority
          />
        </motion.div>

        {/* Progress bar */}
        <motion.div
          className="mt-12 w-80 h-1.5 bg-white/5 rounded-full overflow-hidden"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <motion.div
            className="h-full bg-gradient-to-r from-brand-light/60 via-brand-lighter/80 to-brand-lightest/60 rounded-full"
            animate={{
              x: ['-100%', '100%'],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
