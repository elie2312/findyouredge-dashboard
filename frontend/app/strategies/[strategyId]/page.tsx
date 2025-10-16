'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Header } from '@/components/dashboard/header'
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
import { ArrowLeft, Download, TrendingUp, TrendingDown, Target, Activity, Calendar, X } from 'lucide-react'
import { EquityChart, DrawdownChart, WinLossPie, ProfitLossBar } from '@/components/charts'
import { API_URL } from '@/lib/config'

interface StrategyStats {
  total_trades: number
  total_pnl: number
  winning_trades: number
  losing_trades: number
  winrate: number
  pnl_column?: string
}

interface StrategyData {
  id: string
  name: string
  stats: StrategyStats
  trades: any[]
  columns: string[]
  equity_curve: { trade: number; equity: number }[]
}

export default function StrategyDetailPage() {
  const params = useParams()
  const router = useRouter()
  
  // Gérer les IDs avec slash (ex: MNQ/Opr-trade devient MNQ%2FOpr-trade dans l'URL)
  let strategyId = ''
  if (params.strategyId) {
    if (Array.isArray(params.strategyId)) {
      // Si c'est un tableau, joindre avec /
      strategyId = params.strategyId.join('/')
    } else {
      // Si c'est une string, décoder
      strategyId = decodeURIComponent(params.strategyId)
    }
  }
  
  const [data, setData] = useState<StrategyData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAllTrades, setShowAllTrades] = useState(false)
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')

  useEffect(() => {
    if (strategyId) {
      loadStrategyData()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [strategyId, startDate, endDate])

  const loadStrategyData = async () => {
    if (!strategyId) return
    
    setIsLoading(true)
    setError(null)
    try {
      // Construire l'URL avec les paramètres de date
      let url = `${API_URL}/api/ninja-strategies/${strategyId}/data`
      const params = new URLSearchParams()
      
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      
      if (params.toString()) {
        url += `?${params.toString()}`
      }
      
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des données')
      }
      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue')
    } finally {
      setIsLoading(false)
    }
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

  const handleDownload = async () => {
    if (!strategyId) return
    
    try {
      const response = await fetch(`${API_URL}/api/ninja-strategies/${strategyId}/download`)
      if (!response.ok) {
        throw new Error('Erreur lors du téléchargement')
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${strategyId}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Erreur téléchargement:', err)
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

  if (isLoading) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-violet-500"></div>
            <p className="text-gray-400 mt-4">Chargement...</p>
          </div>
        </div>
      </>
    )
  }

  if (error || !data) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-400 mb-4">{error || 'Données non trouvées'}</p>
            <Button onClick={() => router.push('/strategies')} className="bg-violet-500 hover:bg-violet-600">
              Retour aux stratégies
            </Button>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <Header />
      <div className="min-h-screen">
        <div className="container mx-auto px-6 py-12">
          {/* Header */}
          <div className="mb-8">
            <Button
              onClick={() => router.push('/strategies')}
              variant="ghost"
              className="text-violet-400 hover:text-violet-300 mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Retour aux stratégies
            </Button>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/10 border border-violet-500/30 text-violet-400 rounded-full text-sm font-bold tracking-wider mb-4">
                  <Target className="w-4 h-4" />
                  Détails de la stratégie
                </div>
                <h1 className="text-4xl font-bold text-white mb-2">{data.name}</h1>
              </div>
              <Button
                onClick={handleDownload}
                className="bg-violet-500 hover:bg-violet-600"
              >
                <Download className="w-4 h-4 mr-2" />
                Exporter CSV
              </Button>
            </div>
          </div>

          {/* KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-8">
            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardContent className="pt-6">
                <div className="text-gray-400 text-xs mb-1">Total Trades</div>
                <div className="text-xl font-bold text-white">{data.stats.total_trades}</div>
              </CardContent>
            </Card>
            
            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardContent className="pt-6">
                <div className="text-gray-400 text-xs mb-1">PnL Total</div>
                <div className={`text-xl font-bold ${data.stats.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatPnL(data.stats.total_pnl)}
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardContent className="pt-6">
                <div className="text-gray-400 text-xs mb-1">Winrate</div>
                <div className={`text-xl font-bold ${data.stats.winrate >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                  {data.stats.winrate.toFixed(1)}%
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardContent className="pt-6">
                <div className="text-gray-400 text-xs mb-1">Wins</div>
                <div className="text-xl font-bold text-green-400">{data.stats.winning_trades}</div>
              </CardContent>
            </Card>
            
            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardContent className="pt-6">
                <div className="text-gray-400 text-xs mb-1">Losses</div>
                <div className="text-xl font-bold text-red-400">{data.stats.losing_trades}</div>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardContent className="pt-6">
                <div className="text-gray-400 text-xs mb-1">Avg Win</div>
                <div className="text-xl font-bold text-green-400">
                  {data.stats.winning_trades > 0 
                    ? formatPnL(data.stats.total_pnl / data.stats.winning_trades * (data.stats.winrate / 100))
                    : '$0'}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardContent className="pt-6">
                <div className="text-gray-400 text-xs mb-1">Avg Loss</div>
                <div className="text-xl font-bold text-red-400">
                  {data.stats.losing_trades > 0 
                    ? formatPnL(data.stats.total_pnl / data.stats.losing_trades * ((100 - data.stats.winrate) / 100))
                    : '$0'}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardContent className="pt-6">
                <div className="text-gray-400 text-xs mb-1">Profit Factor</div>
                <div className={`text-xl font-bold ${
                  (data.stats.winning_trades / (data.stats.losing_trades || 1)) >= 1 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {(data.stats.winning_trades / (data.stats.losing_trades || 1)).toFixed(2)}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filtre de date */}
          <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30 mb-8">
            <CardContent className="pt-6">
              <div className="p-4 bg-violet-500/5 border border-violet-400/20 rounded-lg space-y-4">
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
                  </div>
                </div>
                
                <div className="flex flex-wrap items-center gap-4">
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
              </div>
            </CardContent>
          </Card>

          {/* Charts Principaux */}
          <div className="space-y-8 mb-8">
            {data.equity_curve && data.equity_curve.length > 0 && (
              <EquityChart
                data={data.equity_curve.map(item => item.equity)}
                title="Courbe d'Équité"
              />
            )}
          </div>

          {/* Charts Secondaires */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <WinLossPie
              winningTrades={data.stats.winning_trades}
              losingTrades={data.stats.losing_trades}
              title="Répartition Win/Loss"
            />
            <ProfitLossBar
              grossProfit={data.stats.total_pnl > 0 ? data.stats.total_pnl : 0}
              grossLoss={data.stats.total_pnl < 0 ? Math.abs(data.stats.total_pnl) : 0}
              title="Profit vs Loss Brut"
            />
          </div>

          {/* Trades Table */}
          <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <span>Historique des trades</span>
                <Badge variant="outline" className="text-violet-400 border-violet-400/50">
                  {showAllTrades ? data.trades.length : Math.min(20, data.trades.length)} / {data.trades.length} trades
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-violet-400/20 hover:bg-transparent">
                      <TableHead className="text-violet-400 font-bold">#</TableHead>
                      <TableHead className="text-violet-400 font-bold">Sens</TableHead>
                      <TableHead className="text-violet-400 font-bold">Prix Entrée</TableHead>
                      <TableHead className="text-violet-400 font-bold">Prix Sortie</TableHead>
                      <TableHead className="text-violet-400 font-bold">Heure Entrée</TableHead>
                      <TableHead className="text-violet-400 font-bold">Heure Sortie</TableHead>
                      <TableHead className="text-violet-400 font-bold text-right">Profit</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(showAllTrades ? data.trades : data.trades.slice(0, 20)).map((trade, index) => {
                      const actualIndex = showAllTrades ? index : index
                      
                      // Debug: afficher les valeurs du premier trade
                      if (index === 0) {
                        console.log('🔍 Colonnes disponibles:', Object.keys(trade))
                        console.log('🔍 Premier trade complet:', trade)
                        console.log('🔍 Prix d\'entrée:', trade["Prix d'entrée"])
                        console.log('🔍 Heure d\'entrée:', trade["Heure d'entrée"])
                      }
                      
                      // Récupérer les valeurs avec les noms exacts (essayer toutes les variantes)
                      const direction = trade['Pos. marché.'] || '-'
                      
                      // Essayer de trouver la bonne clé pour Prix d'entrée
                      const entryPriceKey = Object.keys(trade).find(k => k.includes('entrée') && k.includes('Prix'))
                      const entryPrice = entryPriceKey ? trade[entryPriceKey] : 'N/A'
                      
                      const exitPrice = trade['Prix de sortie'] || 'N/A'
                      
                      // Essayer de trouver la bonne clé pour Heure d'entrée
                      const entryTimeKey = Object.keys(trade).find(k => k.includes('entrée') && k.includes('Heure'))
                      const entryTime = entryTimeKey ? trade[entryTimeKey] : 'N/A'
                      
                      const exitTime = trade['Heure de sortie'] || 'N/A'
                      const profit = trade['Profit'] || 0
                      
                      // Nettoyer le profit s'il contient des caractères
                      let profitValue = profit
                      if (typeof profit === 'string') {
                        const cleaned = profit.replace(/[^0-9.,-]/g, '').replace(',', '.')
                        profitValue = parseFloat(cleaned) || 0
                      }
                      
                      return (
                        <TableRow key={actualIndex} className="border-violet-400/10 hover:bg-violet-500/5">
                          <TableCell className="text-gray-400">{actualIndex + 1}</TableCell>
                          <TableCell className="text-gray-300">
                            <Badge variant="outline" className={
                              direction === 'Long' || direction === 'Achat' 
                                ? 'text-green-400 border-green-400/50' 
                                : 'text-red-400 border-red-400/50'
                            }>
                              {direction}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-gray-300">{entryPrice}</TableCell>
                          <TableCell className="text-gray-300">{exitPrice}</TableCell>
                          <TableCell className="text-gray-300 text-sm">{entryTime}</TableCell>
                          <TableCell className="text-gray-300 text-sm">{exitTime}</TableCell>
                          <TableCell className={`text-right font-bold ${
                            profitValue >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {typeof profitValue === 'number' ? formatPnL(profitValue) : profit}
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </div>
              
              {data.trades.length > 20 && !showAllTrades && (
                <div className="mt-4 text-center">
                  <Button
                    onClick={() => setShowAllTrades(true)}
                    variant="outline"
                    className="border-violet-400/50 text-violet-400 hover:bg-violet-500/20"
                  >
                    Charger tous les trades ({data.trades.length - 20} restants)
                  </Button>
                </div>
              )}
              
              {showAllTrades && (
                <div className="mt-4 text-center">
                  <Button
                    onClick={() => setShowAllTrades(false)}
                    variant="outline"
                    className="border-violet-400/50 text-violet-400 hover:bg-violet-500/20"
                  >
                    Afficher moins
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}
