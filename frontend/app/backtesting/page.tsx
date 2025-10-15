'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Header } from '@/components/dashboard/header'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Zap, Activity, BarChart3, Target, TrendingUp, TrendingDown, Clock, Eye, X, Play } from 'lucide-react'
import Link from 'next/link'

interface Strategy {
  id: number
  name: string
  description: string
  total_runs: number
  avg_pnl: number
  winrate: number
  status: string
}

interface Run {
  run_id: string
  name: string
  status: string
  started_at: string
  completed_at: string | null
  duration_seconds: number | null
  message: string | null
}

interface Stats {
  total_strategies: number
  total_runs: number
  total_trades: number
  avg_winrate: number
}

export default function BacktestingPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [recentRuns, setRecentRuns] = useState<Run[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [deletingRunId, setDeletingRunId] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setIsLoading(true)
    try {
      const [strategiesRes, runsRes] = await Promise.all([
        fetch('http://localhost:8000/api/strategies'),
        fetch('http://localhost:8000/api/runs?limit=10')
      ])

      const strategiesData = await strategiesRes.json()
      const runsData = await runsRes.json()

      setStrategies(strategiesData.strategies || [])
      setRecentRuns(runsData.runs || [])
      setStats(strategiesData.stats || null)
    } catch (error) {
      console.error('Erreur chargement:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteRun = async (runId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette exécution ?')) {
      return
    }
    setDeletingRunId(runId)
    try {
      await fetch(`http://localhost:8000/api/runs/${runId}`, { method: 'DELETE' })
      await loadData()
    } catch (error) {
      console.error('Erreur suppression:', error)
      alert('Erreur lors de la suppression')
    } finally {
      setDeletingRunId(null)
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
      <Header />
      <div className="min-h-screen">
        <div className="container mx-auto px-6 py-12">
          {/* Page Header */}
          <div className="mb-12 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-500/10 border border-orange-500/30 text-orange-400 rounded-full text-sm font-bold tracking-wider mb-6">
              <Zap className="w-4 h-4" />
              BETA
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              Backtesting <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-400">Live</span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Testez vos stratégies Python et analysez les performances
            </p>
          </div>

          {/* Stats Cards - 3 indicateurs */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400 mb-1">Stratégies Python</p>
                      <p className="text-3xl font-bold text-white">{strategies.length}</p>
                    </div>
                    <Target className="w-8 h-8 text-violet-400" />
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400 mb-1">Runs Exécutés</p>
                      <p className="text-3xl font-bold text-white">{recentRuns.filter(r => r.status === 'completed').length}</p>
                    </div>
                    <Activity className="w-8 h-8 text-green-400" />
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400 mb-1">Runs En Cours</p>
                      <p className="text-3xl font-bold text-white">{recentRuns.filter(r => r.status === 'running').length}</p>
                    </div>
                    <Clock className="w-8 h-8 text-orange-400" />
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Section Lancer une stratégie */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="mb-12">
            <Card className="bg-gradient-to-br from-violet-500/10 to-purple-500/10 border-violet-400/30">
              <CardContent className="pt-12 pb-12 text-center">
                <Target className="w-16 h-16 text-violet-400 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-2">Lancer une Stratégie</h3>
                <p className="text-gray-400 mb-6">
                  Sélectionnez et exécutez vos stratégies de backtesting
                </p>
                <Link href="/run">
                  <Button size="lg" className="bg-violet-500 hover:bg-violet-600">
                    <Play className="w-5 h-5 mr-2" />
                    Lancer une stratégie
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </motion.div>

          {/* Mes Runs */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card className="bg-black/40 backdrop-blur-xl border-violet-400/30">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-violet-400" />
                  Mes Runs
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentRuns.length === 0 ? (
                    <div className="text-center py-12">
                      <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                      <p className="text-gray-400">Aucun run disponible</p>
                      <p className="text-sm text-gray-500 mt-2">Lancez votre première stratégie pour voir les résultats ici</p>
                    </div>
                  ) : (
                    recentRuns.map((run, index) => {
                      const timestamp = run.started_at ? new Date(run.started_at).toLocaleString('fr-FR') : 'Date inconnue'
                      const duration = run.duration_seconds ? `${Math.round(run.duration_seconds)}s` : '-'
                      
                      return (
                        <motion.div key={run.run_id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.6 + index * 0.05 }}
                          className="flex items-center justify-between p-4 bg-violet-500/5 border border-violet-400/20 rounded-lg hover:bg-violet-500/10 transition-all">
                          <div className="flex-1">
                            <h4 className="text-white font-semibold mb-1">{run.name || 'Run sans nom'}</h4>
                            <p className="text-sm text-gray-400">{timestamp}</p>
                          </div>
                          <div className="flex items-center gap-6">
                            <div className="text-right">
                              <p className="text-xs text-gray-400">Durée</p>
                              <p className="text-sm font-bold text-white">{duration}</p>
                            </div>
                            <div className="text-right min-w-[100px]">
                              <p className="text-xs text-gray-400">Message</p>
                              <p className="text-sm text-gray-300 truncate">{run.message || '-'}</p>
                            </div>
                            <Badge variant="outline" className={
                              run.status === 'completed' ? 'text-green-400 border-green-400/50' :
                              run.status === 'running' ? 'text-orange-400 border-orange-400/50' : 'text-red-400 border-red-400/50'
                            }>
                              {run.status}
                            </Badge>
                            <div className="flex gap-2">
                              <Link href={`/results/${run.run_id}`}>
                                <Button size="sm" variant="outline" className="border-violet-400/50 text-violet-400 hover:bg-violet-500/20">
                                  <Eye className="w-4 h-4" />
                                </Button>
                              </Link>
                              <Button size="sm" variant="outline" onClick={() => handleDeleteRun(run.run_id as any)}
                                disabled={deletingRunId === run.run_id as any}
                                className="border-red-400/50 text-red-400 hover:bg-red-500/20">
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </motion.div>
                      )
                    })
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
