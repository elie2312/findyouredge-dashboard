'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Header } from '@/components/dashboard/header'
import { Footer } from '@/components/dashboard/footer'
import { LoadingScreen } from '@/components/loading-screen'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Zap, TrendingUp, Target, Activity, ArrowRight, Sparkles, BarChart3, Clock } from 'lucide-react'
import Link from 'next/link'

interface NinjaStrategy {
  id: string
  name: string
  filename: string
  stats: {
    total_trades: number
    total_pnl: number
    winning_trades: number
    losing_trades: number
    winrate: number
  }
}

export default function Home() {
  const router = useRouter()
  const [ninjaStrategies, setNinjaStrategies] = useState<NinjaStrategy[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [hoveredCard, setHoveredCard] = useState<number | null>(null)

  useEffect(() => {
    loadNinjaStrategies()
  }, [])

  const loadNinjaStrategies = async () => {
    const startTime = Date.now()
    
    try {
      const response = await fetch('http://localhost:8000/api/ninja-strategies')
      const data = await response.json()
      setNinjaStrategies(data.strategies || [])
    } catch (error) {
      console.error('Erreur chargement:', error)
    } finally {
      // Assurer un minimum de 3 secondes d'affichage
      const elapsedTime = Date.now() - startTime
      const remainingTime = Math.max(0, 3000 - elapsedTime)
      
      setTimeout(() => {
        setIsLoading(false)
      }, remainingTime)
    }
  }

  const formatPnL = (pnl: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(pnl)
  }

  return (
    <ProtectedRoute>
      <AnimatePresence mode="wait">
        {isLoading && <LoadingScreen key="loading" />}
      </AnimatePresence>
      
      {!isLoading && (
        <>
          <Header />
          <main className="min-h-screen">
        <div className="container mx-auto px-6 py-12">
          {/* Hero Section */}
          <motion.div 
            className="mb-16 text-center relative overflow-hidden rounded-3xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Animated Background */}
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

            {/* Hero Content */}
            <div className="relative z-10 py-12">
              <motion.div 
                className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/10 border border-violet-500/30 text-violet-400 rounded-full text-sm font-bold tracking-wider mb-6"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2, duration: 0.6 }}
              >
                <motion.div 
                  className="w-2 h-2 bg-violet-400 rounded-full shadow-lg shadow-violet-400/50"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                />
                QUANTITATIVE TRADING PLATFORM
              </motion.div>
              
              <motion.h1 
                className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.8 }}
              >
                <motion.span
                  className="text-violet-400"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6, duration: 0.6 }}
                >
                  Backtesting
                </motion.span>
                <br />
                <motion.span 
                  className="text-5xl md:text-6xl bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8, duration: 0.6 }}
                >
                  Haute Performance
                </motion.span>
              </motion.h1>
              
              <motion.p 
                className="text-xl text-gray-400 max-w-2xl mx-auto mb-8 leading-relaxed"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1, duration: 0.6 }}
              >
                Analysez nos stratégies NinjaTrader et testez de nouvelles approches avec notre plateforme de backtesting avancée.
              </motion.p>

              {/* CTA Buttons */}
              <motion.div
                className="flex items-center justify-center gap-4 flex-wrap"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2, duration: 0.6 }}
              >
                <Link href="/strategies">
                  <Button className="bg-violet-500 hover:bg-violet-600 text-white px-8 py-6 text-lg font-semibold rounded-xl shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50 transition-all duration-300 group">
                    <Target className="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" />
                    Stratégies Ninja
                  </Button>
                </Link>
                
                <div className="relative">
                  <Link href="/backtesting">
                    <Button variant="outline" className="border-2 border-violet-400/50 text-violet-400 hover:bg-violet-500/10 hover:border-violet-400 px-8 py-6 text-lg font-semibold rounded-xl transition-all duration-300 group">
                      <Zap className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
                      Backtesting Live
                    </Button>
                  </Link>
                  <Badge className="absolute -top-2 -right-2 bg-violet-500 text-white border-violet-400 text-xs px-2 py-1 shadow-lg">Beta</Badge>
                </div>
              </motion.div>
            </div>
          </motion.div>

          {/* Stats Section - Métriques clés */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mb-16"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {/* Stat 1 */}
              <motion.div 
                className="relative group"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-brand-light/20 to-brand-lighter/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300" />
                <Card className="relative bg-black/60 backdrop-blur-xl border-brand-light/30 hover:border-brand-light/60 transition-all duration-300">
                  <CardContent className="pt-8 pb-8 text-center">
                    <motion.div 
                      className="text-5xl font-bold bg-gradient-to-r from-brand-light to-brand-lighter bg-clip-text text-transparent mb-2"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5, duration: 0.6 }}
                    >
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.7, duration: 0.5 }}
                      >
                        600+
                      </motion.span>
                    </motion.div>
                    <p className="text-sm text-gray-400 font-medium">Trades Analysés</p>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Stat 2 */}
              <motion.div 
                className="relative group"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5 }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-green-500/20 to-emerald-500/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300" />
                <Card className="relative bg-black/60 backdrop-blur-xl border-green-500/30 hover:border-green-500/60 transition-all duration-300">
                  <CardContent className="pt-8 pb-8 text-center">
                    <motion.div 
                      className="text-5xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent mb-2"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.6, duration: 0.6 }}
                    >
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.8, duration: 0.5 }}
                      >
                        1.65
                      </motion.span>
                    </motion.div>
                    <p className="text-sm text-gray-400 font-medium">Profit Factor</p>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Stat 3 */}
              <motion.div 
                className="relative group"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-brand-lighter/20 to-brand-pale/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300" />
                <Card className="relative bg-black/60 backdrop-blur-xl border-brand-lighter/30 hover:border-brand-lighter/60 transition-all duration-300">
                  <CardContent className="pt-8 pb-8 text-center">
                    <motion.div 
                      className="text-5xl font-bold bg-gradient-to-r from-brand-lighter to-brand-pale bg-clip-text text-transparent mb-2"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.7, duration: 0.6 }}
                    >
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.9, duration: 0.5 }}
                      >
                        20+
                      </motion.span>
                    </motion.div>
                    <p className="text-sm text-gray-400 font-medium">Stratégies Actives</p>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Stat 4 */}
              <motion.div 
                className="relative group"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.7 }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/20 to-amber-500/10 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300" />
                <Card className="relative bg-black/60 backdrop-blur-xl border-orange-500/30 hover:border-orange-500/60 transition-all duration-300">
                  <CardContent className="pt-8 pb-8 text-center">
                    <motion.div 
                      className="text-5xl font-bold bg-gradient-to-r from-orange-400 to-amber-400 bg-clip-text text-transparent mb-2"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.8, duration: 0.6 }}
                    >
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1.0, duration: 0.5 }}
                      >
                        5
                      </motion.span>
                    </motion.div>
                    <p className="text-sm text-gray-400 font-medium">Ans de Data</p>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </motion.div>

          {/* Stratégies Ninja Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="mb-16"
          >
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">Stratégies NinjaTrader</h2>
                <p className="text-gray-400">Analysez les performances de nos stratégies importées</p>
              </div>
              <Link href="/strategies">
                <Button variant="outline" className="border-violet-400/50 text-violet-400 hover:bg-violet-500/20">
                  Voir toutes
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>

            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                  <Card key={i} className="bg-black/40 backdrop-blur-xl border-violet-400/30 animate-pulse">
                    <CardContent className="pt-6 h-48"></CardContent>
                  </Card>
                ))}
              </div>
            ) : ninjaStrategies.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {ninjaStrategies.slice(0, 3).map((strategy, index) => (
                  <motion.div
                    key={strategy.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                  >
                    <Link href={`/strategies/${strategy.id}`}>
                      <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30 hover:border-violet-400/60 transition-all duration-300 hover:shadow-lg hover:shadow-violet-500/20 cursor-pointer group">
                        <CardHeader>
                          <CardTitle className="text-white flex items-center justify-between">
                            <span className="group-hover:text-violet-400 transition-colors">{strategy.name}</span>
                            <Target className="w-5 h-5 text-violet-400" />
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                              <p className="text-xs text-gray-400 mb-1">Total Trades</p>
                              <p className="text-lg font-bold text-white">{strategy.stats.total_trades}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-400 mb-1">Winrate</p>
                              <p className={`text-lg font-bold ${strategy.stats.winrate >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                                {strategy.stats.winrate.toFixed(1)}%
                              </p>
                            </div>
                          </div>
                          <div className="pt-4 border-t border-violet-400/20">
                            <p className="text-xs text-gray-400 mb-1">PnL Total</p>
                            <p className={`text-2xl font-bold ${strategy.stats.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {formatPnL(strategy.stats.total_pnl)}
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  </motion.div>
                ))}
              </div>
            ) : (
              <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
                <CardContent className="pt-6 text-center py-12">
                  <Target className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">Aucune stratégie NinjaTrader trouvée</p>
                  <p className="text-sm text-gray-500 mt-2">Importez vos fichiers CSV dans le dossier ninja_runs</p>
                </CardContent>
              </Card>
            )}
          </motion.div>


          {/* Beta Promotion Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1 }}
          >
            <Card className="bg-gradient-to-br from-violet-950/50 via-purple-950/30 to-violet-950/50 border-violet-400/30 overflow-hidden relative">
              {/* Animated Chart Background */}
              <div className="absolute inset-0 opacity-10">
                {/* Grid */}
                <div className="absolute inset-0 opacity-30" style={{
                  backgroundImage: `
                    linear-gradient(to right, rgba(139, 92, 246, 0.1) 1px, transparent 1px),
                    linear-gradient(to bottom, rgba(139, 92, 246, 0.1) 1px, transparent 1px)
                  `,
                  backgroundSize: '60px 60px',
                }} />
                
                {/* Animated Chart Line */}
                <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400" preserveAspectRatio="xMidYMid slice">
                  <defs>
                    <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.4"/>
                      <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.05"/>
                    </linearGradient>
                  </defs>
                  
                  {/* Chart Area */}
                  <motion.path
                    d="M 0 300 Q 80 260, 160 280 Q 240 300, 320 260 Q 400 220, 480 250 Q 560 280, 640 240 Q 720 200, 800 230 Q 880 260, 960 220 Q 1040 180, 1120 210 Q 1160 225, 1200 200 L 1200 400 L 0 400 Z"
                    fill="url(#chartGradient)"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: [0, 1, 1] }}
                    transition={{ 
                      duration: 2,
                      times: [0, 0.5, 1],
                      ease: "easeInOut"
                    }}
                  />
                  
                  {/* Chart Line - Courbe en vagues */}
                  <motion.path
                    d="M 0 300 Q 80 260, 160 280 Q 240 300, 320 260 Q 400 220, 480 250 Q 560 280, 640 240 Q 720 200, 800 230 Q 880 260, 960 220 Q 1040 180, 1120 210 Q 1160 225, 1200 200"
                    stroke="#8b5cf6"
                    strokeWidth="3"
                    fill="none"
                    strokeDasharray="3000"
                    strokeDashoffset="3000"
                    animate={{ strokeDashoffset: [3000, 0, 0] }}
                    transition={{ 
                      duration: 5,
                      times: [0, 0.8, 1],
                      repeat: Infinity,
                      repeatDelay: 5,
                      ease: [0.43, 0.13, 0.23, 0.96]
                    }}
                  />
                </svg>
                
                {/* Glow Effects */}
                <motion.div
                  className="absolute top-1/4 right-1/4 w-96 h-96 bg-violet-500/20 rounded-full blur-3xl"
                  animate={{ 
                    scale: [1, 1.2, 1],
                    opacity: [0.3, 0.5, 0.3]
                  }}
                  transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                />
                <motion.div
                  className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
                  animate={{ 
                    scale: [1.2, 1, 1.2],
                    opacity: [0.5, 0.3, 0.5]
                  }}
                  transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 2.5 }}
                />
              </div>

              <CardContent className="pt-12 pb-12 relative z-10">
                <div className="max-w-4xl mx-auto text-center">
                  <motion.div
                    className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/20 border border-violet-400/40 text-violet-300 rounded-full text-sm font-bold tracking-wider mb-6"
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Zap className="w-4 h-4" />
                    BETA ACCESS
                  </motion.div>

                  <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                    Backtesting <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-400">Live</span>
                  </h2>
                  
                  <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
                    Testez vos stratégies personnalisées en temps réel avec notre moteur de backtesting avancé. 
                    Analyses détaillées, optimisation automatique, et bien plus encore.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {/* Card 1 - Exécution Rapide */}
                    <motion.div 
                      className="relative bg-black/30 backdrop-blur-sm border border-violet-400/20 rounded-xl p-6 overflow-hidden cursor-pointer"
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.3 }}
                      onHoverStart={() => setHoveredCard(1)}
                      onHoverEnd={() => setHoveredCard(null)}
                    >
                      {/* Animated line on hover */}
                      <svg 
                        className="absolute inset-0 w-full h-full"
                        xmlns="http://www.w3.org/2000/svg" 
                        viewBox="0 0 200 100"
                      >
                        <motion.path
                          d="M 0 80 L 50 60 L 100 70 L 150 40 L 200 50"
                          stroke="#8b5cf6"
                          strokeWidth="2"
                          fill="none"
                          initial={{ pathLength: 0, opacity: 0 }}
                          animate={{ 
                            pathLength: hoveredCard === 1 ? 1 : 0,
                            opacity: hoveredCard === 1 ? 0.3 : 0
                          }}
                          transition={{ duration: 0.8, ease: "easeInOut" }}
                        />
                      </svg>
                      <div className="relative z-10">
                        <Activity className="w-8 h-8 text-violet-400 mx-auto mb-3" />
                        <h3 className="text-white font-bold mb-2">Exécution Rapide</h3>
                        <p className="text-sm text-gray-400">Résultats instantanés sur des années de données</p>
                      </div>
                    </motion.div>
                    
                    {/* Card 2 - Analytics Avancés */}
                    <motion.div 
                      className="relative bg-black/30 backdrop-blur-sm border border-violet-400/20 rounded-xl p-6 overflow-hidden cursor-pointer"
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.3 }}
                      onHoverStart={() => setHoveredCard(2)}
                      onHoverEnd={() => setHoveredCard(null)}
                    >
                      {/* Animated candlestick chart on hover */}
                      <svg 
                        className="absolute inset-0 w-full h-full"
                        xmlns="http://www.w3.org/2000/svg" 
                        viewBox="0 0 200 100"
                      >
                        {/* Candlesticks */}
                        {[
                          { x: 25, high: 30, low: 70, open: 45, close: 55, color: '#8b5cf6' },
                          { x: 50, high: 40, low: 75, open: 60, close: 50, color: '#a78bfa' },
                          { x: 75, high: 35, low: 65, open: 50, close: 45, color: '#c084fc' },
                          { x: 100, high: 25, low: 60, open: 55, close: 35, color: '#8b5cf6' },
                          { x: 125, high: 30, low: 70, open: 40, close: 60, color: '#a78bfa' },
                          { x: 150, high: 20, low: 55, open: 50, close: 30, color: '#c084fc' },
                          { x: 175, high: 25, low: 60, open: 35, close: 50, color: '#8b5cf6' }
                        ].map((candle, i) => (
                          <g key={i}>
                            {/* Wick */}
                            <motion.line
                              x1={candle.x}
                              y1={candle.high}
                              x2={candle.x}
                              y2={candle.low}
                              stroke={candle.color}
                              strokeWidth="1"
                              initial={{ scaleY: 0, opacity: 0 }}
                              animate={{ 
                                scaleY: hoveredCard === 2 ? 1 : 0,
                                opacity: hoveredCard === 2 ? 0.3 : 0
                              }}
                              transition={{ duration: 0.3, delay: hoveredCard === 2 ? i * 0.08 : 0 }}
                              style={{ transformOrigin: 'center' }}
                            />
                            {/* Body */}
                            <motion.rect
                              x={candle.x - 6}
                              y={Math.min(candle.open, candle.close)}
                              width="12"
                              height={Math.abs(candle.close - candle.open)}
                              fill={candle.color}
                              initial={{ scaleY: 0, opacity: 0 }}
                              animate={{ 
                                scaleY: hoveredCard === 2 ? 1 : 0,
                                opacity: hoveredCard === 2 ? 0.25 : 0
                              }}
                              transition={{ duration: 0.3, delay: hoveredCard === 2 ? i * 0.08 : 0 }}
                              style={{ transformOrigin: 'center' }}
                            />
                          </g>
                        ))}
                      </svg>
                      <div className="relative z-10">
                        <BarChart3 className="w-8 h-8 text-violet-400 mx-auto mb-3" />
                        <h3 className="text-white font-bold mb-2">Analytics Avancés</h3>
                        <p className="text-sm text-gray-400">Métriques détaillées et visualisations</p>
                      </div>
                    </motion.div>
                    
                    {/* Card 3 - Optimisation IA */}
                    <motion.div 
                      className="relative bg-black/30 backdrop-blur-sm border border-violet-400/20 rounded-xl p-6 overflow-hidden cursor-pointer"
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.3 }}
                      onHoverStart={() => setHoveredCard(3)}
                      onHoverEnd={() => setHoveredCard(null)}
                    >
                      {/* Animated robot on hover */}
                      <svg 
                        className="absolute inset-0 w-full h-full"
                        xmlns="http://www.w3.org/2000/svg" 
                        viewBox="0 0 200 100"
                      >
                        <motion.g 
                          transform="translate(85, 25)"
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ 
                            opacity: hoveredCard === 3 ? 0.3 : 0,
                            scale: hoveredCard === 3 ? 1 : 0.8
                          }}
                          transition={{ duration: 0.4 }}
                        >
                          {/* Robot Head */}
                          <rect
                            x="0"
                            y="0"
                            width="30"
                            height="25"
                            rx="3"
                            fill="#8b5cf6"
                          />
                          
                          {/* Antenna */}
                          <line
                            x1="15"
                            y1="0"
                            x2="15"
                            y2="-8"
                            stroke="#a78bfa"
                            strokeWidth="2"
                          />
                          <circle
                            cx="15"
                            cy="-8"
                            r="3"
                            fill="#c084fc"
                          />
                          
                          {/* Eyes */}
                          <circle
                            cx="10"
                            cy="10"
                            r="3"
                            fill="#c084fc"
                          />
                          <circle
                            cx="20"
                            cy="10"
                            r="3"
                            fill="#c084fc"
                          />
                          
                          {/* Mouth */}
                          <path
                            d="M 8 18 Q 15 22, 22 18"
                            stroke="#a78bfa"
                            strokeWidth="2"
                            fill="none"
                          />
                          
                          {/* Body */}
                          <rect
                            x="-5"
                            y="25"
                            width="40"
                            height="30"
                            rx="4"
                            fill="#8b5cf6"
                          />
                          
                          {/* Arms */}
                          <rect
                            x="-10"
                            y="30"
                            width="5"
                            height="15"
                            rx="2"
                            fill="#a78bfa"
                          />
                          <rect
                            x="35"
                            y="30"
                            width="5"
                            height="15"
                            rx="2"
                            fill="#a78bfa"
                          />
                          
                          {/* Sparkles around robot */}
                          {[
                            { x: -15, y: 15 },
                            { x: 45, y: 20 },
                            { x: -10, y: 50 },
                            { x: 40, y: 55 }
                          ].map((sparkle, i) => (
                            <motion.path
                              key={i}
                              d={`M ${sparkle.x} ${sparkle.y} l 2 2 l -2 2 l -2 -2 z`}
                              fill="#c084fc"
                              animate={{ 
                                opacity: hoveredCard === 3 ? [0, 0.8, 0] : 0,
                                scale: hoveredCard === 3 ? [0.5, 1.2, 0.5] : 0
                              }}
                              transition={{ 
                                duration: 1.5,
                                delay: i * 0.2,
                                repeat: hoveredCard === 3 ? Infinity : 0,
                                repeatDelay: 0.3
                              }}
                            />
                          ))}
                        </motion.g>
                      </svg>
                      <div className="relative z-10">
                        <Sparkles className="w-8 h-8 text-violet-400 mx-auto mb-3" />
                        <h3 className="text-white font-bold mb-2">Optimisation IA</h3>
                        <p className="text-sm text-gray-400">Trouvez les meilleurs paramètres automatiquement</p>
                      </div>
                    </motion.div>
                  </div>

                  <Link href="/backtesting">
                    <Button size="lg" className="text-lg px-8 py-6 bg-gradient-to-r from-orange-500 to-violet-500 hover:from-orange-400 hover:to-violet-400 text-white font-bold shadow-lg shadow-orange-500/50 hover:shadow-orange-500/70 transition-all duration-300">
                      <Zap className="w-5 h-5 mr-2" />
                      Accéder à la Beta
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </main>
      <Footer />
        </>
      )}
    </ProtectedRoute>
  )
}
