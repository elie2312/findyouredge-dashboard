'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useRuns, useRunResults } from '@/hooks/useRuns'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Header } from '@/components/dashboard/header'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { ArrowLeft, TrendingUp, TrendingDown, BarChart3, Target, Activity, DollarSign, Percent } from 'lucide-react'
import { formatUSD, formatPercent } from '@/lib/utils'
import type { RunResults } from '@/types/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { API_URL } from '@/lib/config'

export default function ComparePage() {
  const router = useRouter()
  const { data: runsData, isLoading } = useRuns()
  const [selectedRuns, setSelectedRuns] = useState<string[]>([])
  const [runsResults, setRunsResults] = useState<Record<string, RunResults>>({})

  const completedRuns = runsData?.runs.filter(r => r.status === 'completed') || []
  
  // Récupérer les résultats pour chaque run sélectionné
  useEffect(() => {
    const fetchResults = async () => {
      for (const runId of selectedRuns) {
        setRunsResults(prev => {
          // Si déjà chargé, ne pas recharger
          if (prev[runId]) return prev
          
          // Lancer le chargement
          fetch(`${API_URL}/api/runs/${runId}/results`)
            .then(response => {
              if (response.ok) {
                return response.json()
              }
              throw new Error('Failed to fetch')
            })
            .then(data => {
              setRunsResults(current => ({ ...current, [runId]: data }))
            })
            .catch(error => {
              console.error(`Erreur récupération résultats ${runId}:`, error)
            })
          
          return prev
        })
      }
    }
    fetchResults()
  }, [selectedRuns])

  const toggleRun = (runId: string) => {
    if (selectedRuns.includes(runId)) {
      setSelectedRuns(selectedRuns.filter(id => id !== runId))
    } else if (selectedRuns.length < 5) {
      setSelectedRuns([...selectedRuns, runId])
    }
  }

  return (
    <ProtectedRoute>
      <Header />
      <div className="min-h-screen">
        <div className="container mx-auto px-6 py-12">
          {/* Page Header */}
          <div className="mb-12 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/10 border border-violet-500/30 text-violet-400 rounded-full text-sm font-bold tracking-wider mb-6">
              <BarChart3 className="w-4 h-4" />
              Analyse Comparative
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              <span className="text-violet-400">Comparer</span> les Backtests
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Sélectionnez jusqu'à 5 runs pour analyser et comparer leurs performances
            </p>
          </div>

          {/* Sélecteur de runs compact */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Sélection des Runs</span>
                <Badge variant="outline">{selectedRuns.length}/5 sélectionnés</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex gap-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-12 w-32 bg-muted animate-pulse rounded" />
                  ))}
                </div>
              ) : completedRuns.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  Aucun run terminé disponible
                </p>
              ) : (
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {completedRuns.map((run) => (
                    <motion.div
                      key={run.run_id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div
                        className={`px-3 py-2 rounded-lg border cursor-pointer transition-all text-sm ${
                          selectedRuns.includes(run.run_id)
                            ? 'bg-primary text-primary-foreground border-primary'
                            : 'hover:bg-muted/50 border-border'
                        } ${
                          !selectedRuns.includes(run.run_id) && selectedRuns.length >= 5
                            ? 'opacity-50 cursor-not-allowed'
                            : ''
                        }`}
                        onClick={() => toggleRun(run.run_id)}
                      >
                        <div className="font-medium truncate max-w-[120px]">
                          {run.name || run.run_id.slice(0, 8)}
                        </div>
                        <div className="text-xs opacity-70">
                          {run.run_id.slice(-8)}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
              {selectedRuns.length > 0 && (
                <div className="mt-4 flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedRuns([])}
                  >
                    Effacer tout
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {selectedRuns.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-4xl mb-4">📊</p>
              <p className="text-muted-foreground">
                Sélectionnez des runs pour voir la comparaison
              </p>
            </div>
          ) : (
            <div className="space-y-8">
              {/* Courbes d'Equity */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Courbes d'Equity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={(() => {
                          // Créer un dataset combiné pour toutes les courbes
                          const maxLength = Math.max(
                            ...selectedRuns.map(runId => runsResults[runId]?.equity_curve?.length || 0)
                          )
                          
                          const combinedData = []
                          for (let i = 0; i < maxLength; i++) {
                            const point: any = { index: i }
                            selectedRuns.forEach(runId => {
                              const results = runsResults[runId]
                              if (results?.equity_curve && results.equity_curve[i] !== undefined) {
                                point[runId.slice(-8)] = results.equity_curve[i]
                              }
                            })
                            combinedData.push(point)
                          }
                          return combinedData
                        })()}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="index"
                          label={{ value: 'Trades', position: 'insideBottom', offset: -5 }}
                        />
                        <YAxis 
                          label={{ value: 'PnL ($)', angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip 
                          formatter={(value, name) => [formatUSD(Number(value)), `Run ${name}`]}
                          labelFormatter={(label) => `Trade ${label}`}
                        />
                        <Legend />
                        {selectedRuns.map((runId, index) => {
                          const results = runsResults[runId]
                          if (!results?.equity_curve) return null
                          
                          const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1']
                          
                          return (
                            <Line
                              key={runId}
                              dataKey={runId.slice(-8)}
                              stroke={colors[index % colors.length]}
                              strokeWidth={2}
                              dot={false}
                              connectNulls={false}
                            />
                          )
                        })}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Métriques en Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {selectedRuns.map((runId, index) => {
                  const results = runsResults[runId]
                  if (!results) return null
                  
                  const colors = [
                    'border-purple-200 bg-purple-50 dark:bg-purple-900/20',
                    'border-green-200 bg-green-50 dark:bg-green-900/20', 
                    'border-fuchsia-200 bg-fuchsia-50 dark:bg-fuchsia-900/20',
                    'border-orange-200 bg-orange-50 dark:bg-orange-900/20',
                    'border-pink-200 bg-pink-50 dark:bg-pink-900/20'
                  ]
                  
                  return (
                    <Card key={runId} className={`${colors[index % colors.length]} border-2`}>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium truncate">
                          {completedRuns.find(r => r.run_id === runId)?.name || runId.slice(0, 8)}
                        </CardTitle>
                        <p className="text-xs text-muted-foreground font-mono">
                          {runId.slice(-8)}
                        </p>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {/* PnL Net */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <DollarSign className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm">PnL Net</span>
                          </div>
                          <span className={`font-bold ${results.metrics.net_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatUSD(results.metrics.net_pnl)}
                          </span>
                        </div>

                        {/* Win Rate */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Percent className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm">Win Rate</span>
                          </div>
                          <span className="font-bold">
                            {formatPercent(results.metrics.win_rate)}
                          </span>
                        </div>

                        {/* Total Trades */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Target className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm">Trades</span>
                          </div>
                          <span className="font-bold">
                            {results.metrics.total_trades}
                          </span>
                        </div>

                        {/* Profit Factor */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Activity className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm">PF</span>
                          </div>
                          <span className="font-bold">
                            {results.metrics.profit_factor > 999 ? '∞' : results.metrics.profit_factor.toFixed(2)}
                          </span>
                        </div>

                        {/* Max Drawdown */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <TrendingDown className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm">Max DD</span>
                          </div>
                          <span className="font-bold text-red-600">
                            {formatUSD(results.metrics.max_drawdown)}
                          </span>
                        </div>

                        {/* Bouton détails */}
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full mt-4"
                          onClick={() => router.push(`/results/${runId}`)}
                        >
                          Voir détails
                        </Button>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>

              {/* Tableau de comparaison détaillé */}
              <Card>
                <CardHeader>
                  <CardTitle>Comparaison Détaillée</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-3 font-semibold">Métrique</th>
                          {selectedRuns.map((runId) => (
                            <th key={runId} className="text-right p-3 font-semibold">
                              <div className="text-xs font-mono truncate max-w-[120px]">
                                {runId.slice(-8)}
                              </div>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b hover:bg-muted/50">
                          <td className="p-3 font-medium">Expectancy</td>
                          {selectedRuns.map((runId) => {
                            const exp = runsResults[runId]?.metrics.expectancy
                            return (
                              <td key={runId} className={`text-right p-3 font-mono ${exp && exp >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {exp !== undefined ? formatUSD(exp) : '-'}
                              </td>
                            )
                          })}
                        </tr>
                        <tr className="border-b hover:bg-muted/50">
                          <td className="p-3 font-medium">Avg Win</td>
                          {selectedRuns.map((runId) => (
                            <td key={runId} className="text-right p-3 font-mono text-green-600">
                              {runsResults[runId] ? formatUSD(runsResults[runId].metrics.avg_win) : '-'}
                            </td>
                          ))}
                        </tr>
                        <tr className="border-b hover:bg-muted/50">
                          <td className="p-3 font-medium">Avg Loss</td>
                          {selectedRuns.map((runId) => (
                            <td key={runId} className="text-right p-3 font-mono text-red-600">
                              {runsResults[runId] ? formatUSD(runsResults[runId].metrics.avg_loss) : '-'}
                            </td>
                          ))}
                        </tr>
                        <tr className="border-b hover:bg-muted/50">
                          <td className="p-3 font-medium">Winning Trades</td>
                          {selectedRuns.map((runId) => (
                            <td key={runId} className="text-right p-3 font-mono">
                              {runsResults[runId]?.metrics.winning_trades || '-'}
                            </td>
                          ))}
                        </tr>
                        <tr className="border-b hover:bg-muted/50">
                          <td className="p-3 font-medium">Losing Trades</td>
                          {selectedRuns.map((runId) => (
                            <td key={runId} className="text-right p-3 font-mono">
                              {runsResults[runId]?.metrics.losing_trades || '-'}
                            </td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  )
}
