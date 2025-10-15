'use client'

import { useRouter } from 'next/navigation'
import { useRunResults } from '@/hooks/useRuns'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { EquityChart, DrawdownChart, WinLossPie, ProfitLossBar } from '@/components/charts'
import { KpiCard } from '@/components/dashboard/kpi-card'
import { Header } from '@/components/dashboard/header'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { ArrowLeft, TrendingUp, TrendingDown, Target, DollarSign, Percent, Activity, BarChart3 } from 'lucide-react'
import { formatUSD, formatPercent } from '@/lib/utils'

export default function ResultsPage({ params }: { params: { runId: string } }) {
  const router = useRouter()
  const { data: results, isLoading, error } = useRunResults(params.runId)

  if (error) {
    return (
      <ProtectedRoute>
        <Header />
        <div className="min-h-screen">
          <div className="container mx-auto px-6 py-12">
            <div className="mb-12 text-center">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#ff4444]/10 border border-[#ff4444]/30 text-[#ff4444] rounded-full text-sm font-bold tracking-wider mb-6">
                <BarChart3 className="w-4 h-4" />
                Erreur de Chargement
              </div>
              <h1 className="text-5xl font-bold text-white mb-4">
                Résultats <span className="text-[#ff4444]">Indisponibles</span>
              </h1>
            </div>
            <Card className="bg-destructive/10 border-destructive">
              <CardContent className="p-6">
                <p className="text-destructive">❌ Erreur lors du chargement des résultats</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </ProtectedRoute>
    )
  }

  if (isLoading) {
    return (
      <ProtectedRoute>
        <Header />
        <div className="min-h-screen">
          <div className="container mx-auto px-6 py-12">
            <div className="mb-12 text-center">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/10 border border-violet-500/30 text-violet-400 rounded-full text-sm font-bold tracking-wider mb-6">
                <BarChart3 className="w-4 h-4" />
                Chargement des Résultats
              </div>
              <h1 className="text-5xl font-bold text-white mb-4">
                Analyse en Cours
              </h1>
            </div>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 bg-muted animate-pulse rounded-lg" />
              ))}
            </div>
          </div>
        </div>
      </ProtectedRoute>
    )
  }

  if (!results) {
    return (
      <ProtectedRoute>
        <Header />
        <div className="min-h-screen">
          <div className="container mx-auto px-6 py-12">
            <Card>
              <CardContent className="p-6">
                <p className="text-muted-foreground">Aucun résultat disponible</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </ProtectedRoute>
    )
  }

  const { metrics } = results

  const formatUSD = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatTime = (dateTimeString: string) => {
    try {
      if (!dateTimeString || dateTimeString === 'N/A' || dateTimeString === '') return '-'
      
      const date = new Date(dateTimeString)
      if (isNaN(date.getTime())) return '-'
      
      // Formater en heure de Paris (UTC+1/+2)
      return date.toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Europe/Paris'
      })
    } catch {
      return '-'
    }
  }

  return (
    <ProtectedRoute>
      <Header />
      <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push('/')}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-4xl font-bold">📈 Résultats du Backtest</h1>
              <p className="text-muted-foreground mt-2">{results.strategy}</p>
            </div>
          </div>
          <Button variant="outline" onClick={() => router.push('/compare')}>
            🔍 Comparer
          </Button>
        </div>

        {/* KPIs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <KpiCard
            title="Total Trades"
            value={metrics.total_trades.toLocaleString()}
            icon={Activity}
            delay={0}
          />
          <KpiCard
            title="Win Rate"
            value={formatPercent(metrics.win_rate)}
            icon={Target}
            trend={{
              value: metrics.win_rate * 100,
              isPositive: metrics.win_rate >= 0.5
            }}
            delay={0.1}
          />
          <KpiCard
            title="PnL Net"
            value={formatUSD(metrics.net_pnl)}
            icon={DollarSign}
            trend={{
              value: metrics.net_pnl,
              isPositive: metrics.net_pnl >= 0
            }}
            delay={0.2}
          />
          <KpiCard
            title="Profit Factor"
            value={metrics.profit_factor === Infinity ? '∞' : metrics.profit_factor.toFixed(2)}
            icon={TrendingUp}
            delay={0.3}
          />
        </div>

        {/* Métriques Secondaires */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <KpiCard
            title="Max Drawdown"
            value={formatUSD(metrics.max_drawdown)}
            icon={TrendingDown}
            trend={{
              value: Math.abs(metrics.max_drawdown),
              isPositive: false
            }}
            delay={0.4}
          />
          <KpiCard
            title="Gain Moyen"
            value={formatUSD(metrics.avg_win)}
            icon={TrendingUp}
            delay={0.5}
          />
          <KpiCard
            title="Perte Moyenne"
            value={formatUSD(metrics.avg_loss)}
            icon={TrendingDown}
            delay={0.6}
          />
          <KpiCard
            title="Expectancy"
            value={formatUSD(metrics.expectancy)}
            icon={Percent}
            trend={{
              value: metrics.expectancy,
              isPositive: metrics.expectancy >= 0
            }}
            delay={0.7}
          />
        </div>

        {/* Charts Principaux */}
        <div className="space-y-8 mb-8">
          {results.equity_curve.length > 0 && (
            <EquityChart
              data={results.equity_curve}
              title="Courbe d'Équité"
            />
          )}

          {results.drawdown_curve.length > 0 && (
            <DrawdownChart
              data={results.drawdown_curve}
              title="Drawdown"
            />
          )}
        </div>

        {/* Charts Secondaires */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <WinLossPie
            winningTrades={metrics.winning_trades}
            losingTrades={metrics.losing_trades}
            title="Répartition Win/Loss"
          />
          <ProfitLossBar
            grossProfit={metrics.gross_profit}
            grossLoss={metrics.gross_loss}
            title="Profit vs Loss Brut"
          />
        </div>


        {/* Récapitulatif des Trades */}
        {results.trades && results.trades.length > 0 && (
          <div className="space-y-6">
            {/* Tableau Récapitulatif */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  📊 Récapitulatif des Trades
                  <span className="text-sm font-normal text-muted-foreground">
                    ({results.trades.length} trades)
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  {/* Trades Gagnants */}
                  <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-green-800 dark:text-green-200">Trades Gagnants</span>
                    </div>
                    <div className="text-2xl font-bold text-green-600">
                      {results.trades.filter(t => t.pnl_usd > 0).length}
                    </div>
                    <div className="text-xs text-green-600">
                      {((results.trades.filter(t => t.pnl_usd > 0).length / results.trades.length) * 100).toFixed(1)}%
                    </div>
                  </div>

                  {/* Trades Perdants */}
                  <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingDown className="w-4 h-4 text-red-600" />
                      <span className="text-sm font-medium text-red-800 dark:text-red-200">Trades Perdants</span>
                    </div>
                    <div className="text-2xl font-bold text-red-600">
                      {results.trades.filter(t => t.pnl_usd < 0).length}
                    </div>
                    <div className="text-xs text-red-600">
                      {((results.trades.filter(t => t.pnl_usd < 0).length / results.trades.length) * 100).toFixed(1)}%
                    </div>
                  </div>

                  {/* Plus Gros Gain */}
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="w-4 h-4 text-purple-600" />
                      <span className="text-sm font-medium text-purple-800 dark:text-purple-200">Plus Gros Gain</span>
                    </div>
                    <div className="text-2xl font-bold text-purple-600">
                      {formatUSD(Math.max(...results.trades.map(t => t.pnl_usd)))}
                    </div>
                    <div className="text-xs text-purple-600">
                      {Math.max(...results.trades.map(t => t.points)).toFixed(2)} pts
                    </div>
                  </div>

                  {/* Plus Grosse Perte */}
                  <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg border border-orange-200 dark:border-orange-800">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity className="w-4 h-4 text-orange-600" />
                      <span className="text-sm font-medium text-orange-800 dark:text-orange-200">Plus Grosse Perte</span>
                    </div>
                    <div className="text-2xl font-bold text-orange-600">
                      {formatUSD(Math.min(...results.trades.map(t => t.pnl_usd)))}
                    </div>
                    <div className="text-xs text-orange-600">
                      {Math.min(...results.trades.map(t => t.points)).toFixed(2)} pts
                    </div>
                  </div>
                </div>

                {/* Statistiques Détaillées */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-muted/30 p-4 rounded-lg">
                    <h4 className="font-semibold mb-3 text-sm">📈 Performance LONG</h4>
                    <div className="space-y-2 text-sm">
                      {(() => {
                        const longTrades = results.trades.filter(t => t.direction === 'LONG')
                        const longWins = longTrades.filter(t => t.pnl_usd > 0).length
                        const longTotal = longTrades.reduce((sum, t) => sum + t.pnl_usd, 0)
                        return (
                          <>
                            <div className="flex justify-between">
                              <span>Trades:</span>
                              <span className="font-medium">{longTrades.length}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Win Rate:</span>
                              <span className="font-medium">
                                {longTrades.length > 0 ? ((longWins / longTrades.length) * 100).toFixed(1) : 0}%
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span>PnL Total:</span>
                              <span className={`font-medium ${longTotal >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatUSD(longTotal)}
                              </span>
                            </div>
                          </>
                        )
                      })()}
                    </div>
                  </div>

                  <div className="bg-muted/30 p-4 rounded-lg">
                    <h4 className="font-semibold mb-3 text-sm">📉 Performance SHORT</h4>
                    <div className="space-y-2 text-sm">
                      {(() => {
                        const shortTrades = results.trades.filter(t => t.direction === 'SHORT')
                        const shortWins = shortTrades.filter(t => t.pnl_usd > 0).length
                        const shortTotal = shortTrades.reduce((sum, t) => sum + t.pnl_usd, 0)
                        return (
                          <>
                            <div className="flex justify-between">
                              <span>Trades:</span>
                              <span className="font-medium">{shortTrades.length}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Win Rate:</span>
                              <span className="font-medium">
                                {shortTrades.length > 0 ? ((shortWins / shortTrades.length) * 100).toFixed(1) : 0}%
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span>PnL Total:</span>
                              <span className={`font-medium ${shortTotal >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatUSD(shortTotal)}
                              </span>
                            </div>
                          </>
                        )
                      })()}
                    </div>
                  </div>

                  <div className="bg-muted/30 p-4 rounded-lg">
                    <h4 className="font-semibold mb-3 text-sm">⚡ Moyennes</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>PnL Moyen:</span>
                        <span className="font-medium">
                          {formatUSD(results.trades.reduce((sum, t) => sum + t.pnl_usd, 0) / results.trades.length)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Gain Moyen:</span>
                        <span className="font-medium text-green-600">
                          {(() => {
                            const wins = results.trades.filter(t => t.pnl_usd > 0)
                            return wins.length > 0 ? formatUSD(wins.reduce((sum, t) => sum + t.pnl_usd, 0) / wins.length) : '$0'
                          })()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Perte Moyenne:</span>
                        <span className="font-medium text-red-600">
                          {(() => {
                            const losses = results.trades.filter(t => t.pnl_usd < 0)
                            return losses.length > 0 ? formatUSD(losses.reduce((sum, t) => sum + t.pnl_usd, 0) / losses.length) : '$0'
                          })()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Détail des Trades */}
            <Card>
              <CardHeader>
                <CardTitle>📋 Détail des Trades</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="text-left p-3 font-semibold">#</th>
                        <th className="text-left p-3 font-semibold">Date</th>
                        <th className="text-left p-3 font-semibold">Heure Entrée</th>
                        <th className="text-center p-3 font-semibold">Direction</th>
                        <th className="text-right p-3 font-semibold">Entry</th>
                        <th className="text-right p-3 font-semibold">Exit</th>
                        <th className="text-right p-3 font-semibold">Points</th>
                        <th className="text-right p-3 font-semibold">PnL</th>
                        <th className="text-center p-3 font-semibold">Résultat</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.trades.slice(0, 100).map((trade, index) => (
                        <tr key={trade.id} className="border-b hover:bg-muted/30 transition-colors">
                          <td className="p-3 text-muted-foreground">{index + 1}</td>
                          <td className="p-3 font-mono text-xs">{trade.date}</td>
                          <td className="p-3 font-mono text-xs text-purple-600">{formatTime(trade.entry_time)}</td>
                          <td className="text-center p-3">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              trade.direction === 'LONG' 
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' 
                                : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                            }`}>
                              {trade.direction}
                            </span>
                          </td>
                          <td className="text-right p-3 font-mono">{trade.entry.toFixed(2)}</td>
                          <td className="text-right p-3 font-mono">{trade.exit.toFixed(2)}</td>
                          <td className={`text-right p-3 font-mono ${trade.points >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {trade.points > 0 ? '+' : ''}{trade.points.toFixed(2)}
                          </td>
                          <td className={`text-right p-3 font-semibold ${trade.pnl_usd >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {trade.pnl_usd > 0 ? '+' : ''}{formatUSD(trade.pnl_usd)}
                          </td>
                          <td className="text-center p-3">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              trade.pnl_usd > 0 
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' 
                                : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                            }`}>
                              {trade.pnl_usd > 0 ? '✅ WIN' : '❌ LOSS'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {results.trades.length > 100 && (
                    <div className="text-center mt-6 p-4 bg-muted/30 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-2">
                        Affichage de 100 trades sur {results.trades.length} total
                      </p>
                      <Button variant="outline" size="sm">
                        📊 Voir tous les trades
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Fichiers de sortie */}
        {results.files.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>📁 Fichiers de Sortie</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {results.files.map((file) => (
                  <div key={file} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm font-mono">{file}</span>
                    <Button variant="outline" size="sm">
                      ⬇️ Télécharger
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
      </div>
    </ProtectedRoute>
  )
}
