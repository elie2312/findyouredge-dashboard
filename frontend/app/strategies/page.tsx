'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { Header } from '@/components/dashboard/header'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Target, Download, TrendingUp, TrendingDown, Activity, Eye, Calendar, X } from 'lucide-react'

interface StrategyStats {
  total_trades: number
  total_pnl: number
  winning_trades: number
  losing_trades: number
  winrate: number
}

interface Strategy {
  id: string
  name: string
  filename: string
  market?: string
  stats: StrategyStats
  error?: string
}

export default function StrategiesPage() {
  const router = useRouter()
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [markets, setMarkets] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')
  const [selectedMarket, setSelectedMarket] = useState<string>('')
  const [showAdvancedDate, setShowAdvancedDate] = useState<boolean>(false)

  useEffect(() => {
    loadStrategies()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startDate, endDate, selectedMarket])

  const loadStrategies = async () => {
    setIsLoading(true)
    setError(null)
    try {
      // Construire l'URL avec les paramètres de date
      let url = 'http://localhost:8000/api/ninja-strategies'
      const params = new URLSearchParams()
      
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      if (selectedMarket) params.append('market', selectedMarket)
      
      if (params.toString()) {
        url += `?${params.toString()}`
      }
      
      console.log('🔍 Chargement des stratégies avec URL:', url)
      console.log('📅 Dates:', { startDate, endDate })
      console.log('📊 Marché:', selectedMarket)
      
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des stratégies')
      }
      const data = await response.json()
      setStrategies(data.strategies || [])
      setMarkets(data.markets || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownload = async (strategyId: string, filename: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/ninja-strategies/${strategyId}/download`)
      if (!response.ok) {
        throw new Error('Erreur lors du téléchargement')
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Erreur téléchargement:', err)
    }
  }

  const formatPnL = (pnl: number) => {
    const formatted = new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(pnl)
    return formatted
  }

  const setQuickDateRange = (range: 'week' | 'month' | 'year') => {
    const today = new Date()
    const end = today.toISOString().split('T')[0]
    let start = new Date()
    
    switch (range) {
      case 'week':
        start.setDate(today.getDate() - 7)
        break
      case 'month':
        start.setMonth(today.getMonth() - 1)
        break
      case 'year':
        start.setFullYear(today.getFullYear() - 1)
        break
    }
    
    setStartDate(start.toISOString().split('T')[0])
    setEndDate(end)
  }

  return (
    <ProtectedRoute>
      <Header />
      <div className="min-h-screen">
        <div className="container mx-auto px-6 py-12">
          {/* Page Header */}
          <div className="mb-12 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/10 border border-violet-500/30 text-violet-400 rounded-full text-sm font-bold tracking-wider mb-6">
              <Target className="w-4 h-4" />
              Stratégies Ninja
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              Stratégies
            </h1>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Consultez les résultats de vos stratégies Ninja Trader
            </p>
          </div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardHeader>
                <CardTitle className="text-white flex items-center justify-between">
                  <span>Résultats des stratégies</span>
                  <Badge variant="outline" className="text-violet-400 border-violet-400/50">
                    {strategies.length} stratégie{strategies.length > 1 ? 's' : ''}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {/* Filtres */}
                <div className="mb-6 p-4 bg-violet-500/5 border border-violet-400/20 rounded-lg space-y-4">
                  {/* Filtre Marché */}
                  {markets.length > 0 && (
                    <div className="flex flex-wrap items-center gap-4 pb-4 border-b border-violet-400/20">
                      <div className="flex items-center gap-2">
                        <Target className="w-5 h-5 text-violet-400" />
                        <span className="text-sm font-medium text-white">Marché :</span>
                      </div>
                      <select
                        value={selectedMarket}
                        onChange={(e) => setSelectedMarket(e.target.value)}
                        className="px-4 py-2 bg-black/40 border border-violet-400/30 rounded-lg text-white text-sm focus:outline-none focus:border-violet-400 transition-colors"
                      >
                        <option value="">Tous les marchés</option>
                        {markets.map((market) => (
                          <option key={market} value={market}>
                            {market}
                          </option>
                        ))}
                      </select>
                      {selectedMarket && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setSelectedMarket('')}
                          className="border-red-400/50 text-red-400 hover:bg-red-500/20"
                        >
                          <X className="w-4 h-4 mr-1" />
                          Réinitialiser marché
                        </Button>
                      )}
                    </div>
                  )}
                  
                  {/* Filtre Date */}
                  <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-violet-400" />
                      <span className="text-sm font-medium text-white">Filtrer par date :</span>
                    </div>
                    
                    {/* Sélections rapides */}
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setQuickDateRange('week')}
                        className="border-violet-400/50 text-violet-400 hover:bg-violet-500/20"
                      >
                        7 derniers jours
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setQuickDateRange('month')}
                        className="border-violet-400/50 text-violet-400 hover:bg-violet-500/20"
                      >
                        Dernier mois
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setQuickDateRange('year')}
                        className="border-violet-400/50 text-violet-400 hover:bg-violet-500/20"
                      >
                        Dernière année
                      </Button>
                      
                      {/* Bouton Date Avancée */}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setShowAdvancedDate(!showAdvancedDate)}
                        className={`${
                          showAdvancedDate 
                            ? 'border-violet-400 bg-violet-500/20 text-violet-300' 
                            : 'border-violet-400/50 text-violet-400'
                        } hover:bg-violet-500/20`}
                      >
                        <Calendar className="w-4 h-4 mr-1" />
                        Date avancée
                      </Button>
                    </div>
                  </div>
                  
                  {/* Inputs de date personnalisés - Affichés uniquement si showAdvancedDate est true */}
                  {showAdvancedDate && (
                    <div className="flex flex-wrap items-center gap-4 pt-4 border-t border-violet-400/20">
                      <div className="flex items-center gap-2">
                        <label className="text-sm text-gray-400">Du</label>
                        <input
                          type="date"
                          value={startDate}
                          onChange={(e) => setStartDate(e.target.value)}
                          className="px-3 py-2 bg-black/40 border border-violet-400/30 rounded-lg text-white text-sm focus:outline-none focus:border-violet-400 transition-colors"
                        />
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <label className="text-sm text-gray-400">Au</label>
                        <input
                          type="date"
                          value={endDate}
                          onChange={(e) => setEndDate(e.target.value)}
                          className="px-3 py-2 bg-black/40 border border-violet-400/30 rounded-lg text-white text-sm focus:outline-none focus:border-violet-400 transition-colors"
                        />
                      </div>
                      
                      {(startDate || endDate) && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setStartDate('')
                            setEndDate('')
                          }}
                          className="border-red-400/50 text-red-400 hover:bg-red-500/20"
                        >
                          <X className="w-4 h-4 mr-1" />
                          Réinitialiser
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
              <CardContent>
                {isLoading ? (
                  <div className="text-center py-12">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-violet-500"></div>
                    <p className="text-gray-400 mt-4">Chargement...</p>
                  </div>
                ) : error ? (
                  <div className="text-center py-12">
                    <p className="text-red-400">{error}</p>
                    <Button
                      onClick={loadStrategies}
                      className="mt-4 bg-violet-500 hover:bg-violet-600"
                    >
                      Réessayer
                    </Button>
                  </div>
                ) : strategies.length === 0 ? (
                  <div className="text-center py-12">
                    <Target className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">Aucune stratégie trouvée dans le dossier ninja_runs</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow className="border-violet-400/20 hover:bg-transparent">
                          <TableHead className="text-violet-400 font-bold">Stratégie</TableHead>
                          <TableHead className="text-violet-400 font-bold text-right">Trades</TableHead>
                          <TableHead className="text-violet-400 font-bold text-right">PnL Total</TableHead>
                          <TableHead className="text-violet-400 font-bold text-right">Winrate</TableHead>
                          <TableHead className="text-violet-400 font-bold text-right">W/L</TableHead>
                          <TableHead className="text-violet-400 font-bold text-center">Action</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {strategies.map((strategy, index) => (
                          <motion.tr
                            key={strategy.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="border-violet-400/10 hover:bg-violet-500/5 transition-colors"
                          >
                            <TableCell className="font-medium text-white">
                              <button
                                onClick={() => router.push(`/strategies/${encodeURIComponent(strategy.id)}`)}
                                className="flex items-center gap-2 hover:text-violet-400 transition-colors group"
                              >
                                <Activity className="w-4 h-4 text-violet-400" />
                                <span className="group-hover:underline">{strategy.name}</span>
                                {strategy.market && (
                                  <Badge variant="outline" className="text-xs text-violet-400 border-violet-400/50 ml-2">
                                    {strategy.market}
                                  </Badge>
                                )}
                                <Eye className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                              </button>
                              {strategy.error && (
                                <p className="text-xs text-red-400 mt-1">Erreur: {strategy.error}</p>
                              )}
                            </TableCell>
                            <TableCell className="text-right text-gray-300">
                              {strategy.stats.total_trades}
                            </TableCell>
                            <TableCell className="text-right">
                              <span className={strategy.stats.total_pnl >= 0 ? 'text-green-400 font-bold' : 'text-red-400 font-bold'}>
                                {strategy.stats.total_pnl >= 0 ? (
                                  <TrendingUp className="w-4 h-4 inline mr-1" />
                                ) : (
                                  <TrendingDown className="w-4 h-4 inline mr-1" />
                                )}
                                {formatPnL(strategy.stats.total_pnl)}
                              </span>
                            </TableCell>
                            <TableCell className="text-right">
                              <Badge
                                variant="outline"
                                className={`${
                                  strategy.stats.winrate >= 50
                                    ? 'text-green-400 border-green-400/50 bg-green-400/10'
                                    : 'text-red-400 border-red-400/50 bg-red-400/10'
                                }`}
                              >
                                {strategy.stats.winrate.toFixed(1)}%
                              </Badge>
                            </TableCell>
                            <TableCell className="text-right text-gray-300">
                              <span className="text-green-400">{strategy.stats.winning_trades}</span>
                              {' / '}
                              <span className="text-red-400">{strategy.stats.losing_trades}</span>
                            </TableCell>
                            <TableCell className="text-center">
                              <div className="flex items-center justify-center gap-2">
                                <Button
                                  onClick={() => router.push(`/strategies/${strategy.id}`)}
                                  size="sm"
                                  variant="outline"
                                  className="border-violet-400/50 text-violet-400 hover:bg-violet-500/20 hover:text-violet-300"
                                >
                                  <Eye className="w-4 h-4 mr-2" />
                                  Détails
                                </Button>
                                <Button
                                  onClick={() => handleDownload(strategy.id, strategy.filename)}
                                  size="sm"
                                  variant="outline"
                                  className="border-violet-400/50 text-violet-400 hover:bg-violet-500/20 hover:text-violet-300"
                                >
                                  <Download className="w-4 h-4 mr-2" />
                                  CSV
                                </Button>
                              </div>
                            </TableCell>
                          </motion.tr>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
