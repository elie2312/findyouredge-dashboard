'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRuns } from '@/hooks/useRuns'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Header } from '@/components/dashboard/header'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { BarChart3, Calendar, Clock, TrendingUp, Target, Activity } from 'lucide-react'
import { formatUSD, formatPercent } from '@/lib/utils'

interface HeatmapData {
  day: string
  hour: number
  value: number
  trades: number
  winRate: number
}

export default function AnalyticsPage() {
  const { data: runsData, isLoading } = useRuns()
  const [selectedRunId, setSelectedRunId] = useState<string>('')
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([])
  const [isLoadingHeatmap, setIsLoadingHeatmap] = useState(false)

  const completedRuns = runsData?.runs.filter(r => r.status === 'completed') || []

  // Charger les données de heatmap pour un run
  const loadHeatmapData = async (runId: string) => {
    if (!runId) return
    
    setIsLoadingHeatmap(true)
    try {
      console.log(`🔍 Chargement heatmap pour run: ${runId}`)
      const response = await fetch(`http://localhost:8000/api/runs/${runId}/heatmap`)
      
      if (response.ok) {
        const data = await response.json()
        console.log(`🔍 Données reçues:`, data)
        setHeatmapData(data.heatmap || [])
      } else {
        const errorText = await response.text()
        console.error(`❌ Erreur HTTP ${response.status}:`, errorText)
      }
    } catch (error) {
      console.error('❌ Erreur chargement heatmap:', error)
    } finally {
      setIsLoadingHeatmap(false)
    }
  }

  useEffect(() => {
    if (selectedRunId) {
      loadHeatmapData(selectedRunId)
    }
  }, [selectedRunId])

  // Auto-sélectionner le premier run
  useEffect(() => {
    if (completedRuns.length > 0 && !selectedRunId) {
      setSelectedRunId(completedRuns[0].run_id)
    }
  }, [completedRuns, selectedRunId])

  const getColorIntensity = (value: number, maxValue: number) => {
    if (maxValue === 0) return 'bg-gray-100'
    const intensity = Math.abs(value) / maxValue
    if (value > 0) {
      // Vert pour positif
      if (intensity > 0.8) return 'bg-green-600'
      if (intensity > 0.6) return 'bg-green-500'
      if (intensity > 0.4) return 'bg-green-400'
      if (intensity > 0.2) return 'bg-green-300'
      return 'bg-green-200'
    } else if (value < 0) {
      // Rouge pour négatif
      if (intensity > 0.8) return 'bg-red-600'
      if (intensity > 0.6) return 'bg-red-500'
      if (intensity > 0.4) return 'bg-red-400'
      if (intensity > 0.2) return 'bg-red-300'
      return 'bg-red-200'
    }
    return 'bg-gray-100'
  }

  const days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven']
  const hours = Array.from({ length: 24 }, (_, i) => i)
  const maxValue = Math.max(...heatmapData.map(d => Math.abs(d.value)))

  return (
    <ProtectedRoute>
      <Header />
      <div className="min-h-screen">
        <div className="container mx-auto px-6 py-12">
          {/* Page Header */}
          <div className="mb-12 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/10 border border-violet-500/30 text-violet-400 rounded-full text-sm font-bold tracking-wider mb-6">
              <BarChart3 className="w-4 h-4" />
              Analytics Avancées
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              Heatmap de <span className="text-violet-400">Performance</span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Analysez vos performances par jour et heure pour identifier les patterns optimaux
            </p>
          </div>

          {/* Sélecteur de Run */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Sélection du Run à Analyser
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex gap-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-10 w-32 bg-muted animate-pulse rounded" />
                  ))}
                </div>
              ) : completedRuns.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">
                  Aucun run terminé disponible
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {completedRuns.map((run) => (
                    <Button
                      key={run.run_id}
                      variant={selectedRunId === run.run_id ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedRunId(run.run_id)}
                      className="flex flex-col items-start p-3 h-auto"
                    >
                      <div className="font-medium truncate max-w-[120px]">
                        {run.name || run.run_id.slice(0, 8)}
                      </div>
                      <div className="text-xs opacity-70">
                        {run.run_id.slice(-8)}
                      </div>
                    </Button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Heatmap */}
          {selectedRunId && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              {/* Heatmap Principal */}
              <div className="lg:col-span-3">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Calendar className="w-5 h-5" />
                      Performance par Jour/Heure
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">
                      PnL moyen par créneau horaire (UTC)
                    </p>
                  </CardHeader>
                  <CardContent>
                    {isLoadingHeatmap ? (
                      <div className="h-64 bg-muted animate-pulse rounded" />
                    ) : (
                      <div className="space-y-4">
                        {/* Légende */}
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-2">
                            <div className="w-4 h-4 bg-red-500 rounded"></div>
                            <span>Pertes</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-4 h-4 bg-gray-100 rounded"></div>
                            <span>Neutre</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-4 h-4 bg-green-500 rounded"></div>
                            <span>Gains</span>
                          </div>
                        </div>

                        {/* Grille Heatmap */}
                        <div className="overflow-x-auto">
                          <div className="inline-block min-w-full">
                            {/* Headers heures */}
                            <div className="flex">
                              <div className="w-12"></div>
                              {hours.map(hour => (
                                <div key={hour} className="w-8 h-6 text-xs text-center text-muted-foreground">
                                  {hour}
                                </div>
                              ))}
                            </div>
                            
                            {/* Lignes jours */}
                            {days.map((day, dayIndex) => (
                              <div key={day} className="flex items-center">
                                <div className="w-12 text-xs text-right pr-2 text-muted-foreground">
                                  {day}
                                </div>
                                {hours.map(hour => {
                                  const dataPoint = heatmapData.find(d => 
                                    d.day === day && d.hour === hour
                                  )
                                  const value = dataPoint?.value || 0
                                  const trades = dataPoint?.trades || 0
                                  
                                  return (
                                    <div
                                      key={`${day}-${hour}`}
                                      className={`w-8 h-8 m-0.5 rounded cursor-pointer transition-all hover:scale-110 ${getColorIntensity(value, maxValue)}`}
                                      title={`${day} ${hour}h: ${formatUSD(value)} (${trades} trades)`}
                                    />
                                  )
                                })}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Statistiques */}
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Activity className="w-4 h-4" />
                      Statistiques
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {formatUSD(heatmapData.reduce((sum, d) => sum + d.value, 0))}
                      </div>
                      <div className="text-xs text-muted-foreground">PnL Total</div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {heatmapData.reduce((sum, d) => sum + d.trades, 0)}
                      </div>
                      <div className="text-xs text-muted-foreground">Total Trades</div>
                    </div>

                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {heatmapData.length > 0 ? 
                          formatPercent(heatmapData.reduce((sum, d) => sum + d.winRate * d.trades, 0) / heatmapData.reduce((sum, d) => sum + d.trades, 0) || 0)
                          : '0%'
                        }
                      </div>
                      <div className="text-xs text-muted-foreground">Win Rate Moyen</div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Clock className="w-4 h-4" />
                      Meilleurs Créneaux
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {heatmapData
                        .filter(d => d.trades > 0)
                        .sort((a, b) => b.value - a.value)
                        .slice(0, 5)
                        .map((slot, index) => (
                          <div key={`${slot.day}-${slot.hour}`} className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">
                                #{index + 1}
                              </Badge>
                              <span>{slot.day} {slot.hour}h</span>
                            </div>
                            <div className="text-right">
                              <div className={`font-medium ${slot.value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatUSD(slot.value)}
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {slot.trades} trades
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  )
}
