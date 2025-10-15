'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter, useSearchParams } from 'next/navigation'
import { useStrategies } from '@/hooks/useStrategies'
import { useRuns } from '@/hooks/useRuns'
import { useDataRange } from '@/hooks/useDataRange'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { StatusBadge } from '@/components/dashboard/status-badge'
import { Header } from '@/components/dashboard/header'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { Play, Calendar, Settings, Loader2, Eye, Target, Activity, Filter } from 'lucide-react'
import type { Strategy } from '@/types/api'

export default function RunPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { data: strategiesData, isLoading } = useStrategies()
  const { data: dataRange } = useDataRange()
  
  // État pour gérer le loading et les runs
  const [isCreatingRun, setIsCreatingRun] = useState(false)
  const [runStatus, setRunStatus] = useState<any>(null)
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)
  
  // Fonction pour vérifier le statut d'un run
  const checkRunStatus = async (runId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/runs/${runId}/status`)
      if (response.ok) {
        const status = await response.json()
        setRunStatus(status)
        
        // Si le run est terminé, arrêter le polling
        if (status.status === 'completed' || status.status === 'failed') {
          if (pollingInterval) {
            clearInterval(pollingInterval)
            setPollingInterval(null)
          }
        }
        
        return status
      }
    } catch (error) {
      console.error('Erreur vérification statut:', error)
    }
  }
  
  // Fonction pour créer un run
  const createRun = async (params: any) => {
    setIsCreatingRun(true)
    try {
      const response = await fetch('http://localhost:8000/api/runs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
      })
      
      if (!response.ok) {
        throw new Error('Erreur lors de la création du run')
      }
      
      const result = await response.json()
      return result
    } finally {
      setIsCreatingRun(false)
    }
  }
  
  // Nettoyer le polling quand le composant se démonte
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
  }, [pollingInterval])
  
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null)
  const [currentRunId, setCurrentRunId] = useState<string | null>(null)
  const [parameters, setParameters] = useState<Record<string, any>>({})
  const [periodType, setPeriodType] = useState<'all' | 'last_month' | 'experimental' | 'custom'>('all')
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [backtestName, setBacktestName] = useState<string>('')
  const [selectedCategory, setSelectedCategory] = useState<string>('Tous')
  const [searchQuery, setSearchQuery] = useState<string>('')

  // Logique de filtrage des stratégies
  const filteredStrategies = strategiesData?.strategies.filter(strategy => {
    // Filtre par catégorie
    const matchesCategory = selectedCategory === 'Tous' || strategy.category === selectedCategory

    // Filtre par recherche texte (nom ou description)
    const matchesSearch = searchQuery === '' ||
      strategy.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      strategy.description.toLowerCase().includes(searchQuery.toLowerCase())

    return matchesCategory && matchesSearch
  }) || []

  // Récupérer les catégories uniques
  const categories = strategiesData ? ['Tous', ...Array.from(new Set(strategiesData.strategies.map(s => s.category)))] : ['Tous']

  // Debug logs
  useEffect(() => {
    if (strategiesData) {
      console.log('🔍 Stratégies chargées:', strategiesData.strategies.length)
      console.log('📂 Catégories disponibles:', categories)
      console.log('🔎 Stratégies filtrées:', filteredStrategies.length)
      console.log('🎯 Filtre sélectionné:', selectedCategory)
      console.log('🔍 Recherche:', searchQuery)
    }
  }, [strategiesData, selectedCategory, searchQuery, filteredStrategies])

  const handleStrategySelect = (strategy: Strategy) => {
    setSelectedStrategy(strategy)
    setParameters({ ...strategy.parameters })
    setShowAdvanced(false)
  }

  useEffect(() => {
    const strategyId = searchParams.get('strategy')
    if (strategyId && strategiesData && !selectedStrategy) {
      const strategy = strategiesData.strategies.find(s => s.id === strategyId)
      if (strategy) {
        setSelectedStrategy(strategy)
        setParameters({ ...strategy.parameters })
        setShowAdvanced(false)
      }
    }
  }, [searchParams, strategiesData, selectedStrategy])

  const getDateRange = () => {
    // Debug pour voir les données disponibles
    console.log('🔍🔍🔍 DEBUT getDateRange')
    console.log('🔍 periodType:', periodType)
    if (dataRange) {
      console.log('✅ DataRange disponible:', dataRange)
      console.log('   - start_date:', dataRange.start_date)
      console.log('   - end_date:', dataRange.end_date)
      console.log('   - total_days:', dataRange.total_days)
    } else {
      console.log('❌ Pas de dataRange disponible - utilisation du fallback')
    }
    
    switch (periodType) {
      case 'all':
        return { start: '', end: '' }
      
      case 'last_month':
        // Dernier mois des données disponibles (en partant de la fin des données CSV)
        if (dataRange) {
          const endDate = new Date(dataRange.end_date)
          const startDate = new Date(endDate)
          startDate.setMonth(endDate.getMonth() - 1)
          
          return {
            start: startDate.toISOString().split('T')[0],
            end: dataRange.end_date
          }
        }
        // Fallback si pas de données
        return {
          start: '2024-09-01',
          end: '2024-09-30'
        }
      
      case 'experimental':
        // Test rapide : dernières 2 semaines des données disponibles
        if (dataRange) {
          const endDate = new Date(dataRange.end_date)
          const startDate = new Date(endDate)
          startDate.setDate(endDate.getDate() - 14) // 2 semaines
          
          return {
            start: startDate.toISOString().split('T')[0],
            end: dataRange.end_date
          }
        }
        // Fallback si pas de données
        return {
          start: '2024-08-14',
          end: '2024-08-21'
        }
      
      case 'custom':
        return { start: startDate, end: endDate }
      
      default:
        return { start: '', end: '' }
    }
  }

  const handleRun = async () => {
    if (!selectedStrategy) return

    try {
      const dateRange = getDateRange()
      const runParams = { ...parameters }
      if (dateRange.start) runParams.START_DATE = dateRange.start
      if (dateRange.end) runParams.END_DATE = dateRange.end

      // Debug: afficher les paramètres envoyés
      console.log('🚀 Lancement backtest:', {
        strategy: selectedStrategy.name,
        periodType,
        dateRange,
        runParams,
        backtestName
      })

      const result = await createRun({
        strategy_id: selectedStrategy.id,
        parameters: runParams,
        name: backtestName || undefined,
      })
      
      setCurrentRunId(result.run_id)
      
      // Démarrer le polling du statut
      const interval = setInterval(() => {
        checkRunStatus(result.run_id)
      }, 2000) // Vérifier toutes les 2 secondes
      
      setPollingInterval(interval)
      
      // Première vérification immédiate
      checkRunStatus(result.run_id)
    } catch (error) {
      console.error('Erreur lancement:', error)
    }
  }

  return (
    <ProtectedRoute>
      <Header />
      <div className="min-h-screen">
        <div className="container mx-auto px-6 py-12">
          <div className="mb-12 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/10 border border-violet-500/30 text-violet-400 rounded-full text-sm font-bold tracking-wider mb-6">
              <Settings className="w-4 h-4" />
              Configuration de Backtest
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              <span className="text-violet-400">Lancer</span> un Backtest
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Sélectionnez une stratégie, configurez les paramètres et lancez votre analyse
            </p>
          </div>

          {/* Sélection de stratégie EN HAUT */}
          <Card className="mb-8 bg-[#1a1a24] border-violet-500/20">
            <CardHeader>
              <CardTitle className="text-xl text-white flex items-center gap-2">
                <Target className="w-6 h-6 text-violet-400" />
                Étape 1 : Sélectionnez une Stratégie
              </CardTitle>
              <p className="text-sm text-gray-400">
                Choisissez la stratégie de trading que vous souhaitez backtester
              </p>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="p-4 border border-violet-500/20 rounded-lg animate-pulse bg-black/40">
                      <div className="h-4 bg-violet-500/10 rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-violet-500/10 rounded w-1/2"></div>
                    </div>
                  ))}
                </div>
              ) : (
                <>
                  {/* Barre de filtres */}
                  <div className="mb-6 p-4 bg-black/40 border border-violet-500/20 rounded-lg">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex items-center gap-2">
                        <Filter className="w-5 h-5 text-violet-400" />
                        <span className="text-sm font-medium text-white">Filtres :</span>
                      </div>
                      <div className="flex items-center gap-2 flex-wrap">
                        {categories.map(category => (
                          <Button
                            key={category}
                            variant={selectedCategory === category ? "default" : "outline"}
                            size="sm"
                            onClick={() => setSelectedCategory(category)}
                            className={`text-xs ${
                              selectedCategory === category
                                ? 'bg-violet-500 text-white border-violet-500'
                                : 'bg-black/40 text-gray-300 border-violet-500/20 hover:bg-violet-500/10 hover:border-violet-500/50'
                            }`}
                          >
                            {category}
                          </Button>
                        ))}
                      </div>
                    </div>

                    {/* Champ de recherche */}
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        placeholder="Rechercher une stratégie..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="flex-1 px-3 py-2 text-sm bg-black/40 border border-violet-500/30 rounded-md text-white placeholder:text-gray-500 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500"
                      />
                      {searchQuery && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSearchQuery('')}
                          className="text-gray-400 hover:text-white"
                        >
                          ✕
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Grille des stratégies filtrées */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredStrategies.length > 0 ? (
                      filteredStrategies.map((strategy, index) => (
                        <motion.div
                          key={strategy.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.05 }}
                          onClick={() => handleStrategySelect(strategy)}
                          className={`p-5 border rounded-xl cursor-pointer transition-all ${
                            selectedStrategy?.id === strategy.id
                              ? 'bg-violet-500/20 border-violet-500 shadow-lg shadow-violet-500/20 scale-105'
                              : 'bg-black/40 border-violet-500/20 hover:border-violet-500/50 hover:bg-violet-500/10 hover:scale-102'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <h4 className="font-semibold text-base text-white">{strategy.name}</h4>
                            {selectedStrategy?.id === strategy.id && (
                              <Badge className="text-xs bg-[#00ff88]/20 text-[#00ff88] border border-[#00ff88]/30">✓ Sélectionné</Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                            {strategy.description}
                          </p>
                          <div className="flex gap-2 mb-3">
                            <Badge variant="outline" className="text-xs bg-violet-500/10 text-violet-400 border-violet-500/30 font-mono">
                              {strategy.timeframe}
                            </Badge>
                            <Badge variant="outline" className="text-xs bg-violet-500/10 text-violet-400 border-violet-500/30 font-mono">
                              {strategy.risk_model}
                            </Badge>
                          </div>
                          <div className="flex gap-1 flex-wrap">
                            <Badge variant="secondary" className="text-xs bg-blue-500/10 text-blue-400 border-blue-500/30">
                              {strategy.category}
                            </Badge>
                            {strategy.tags.slice(0, 2).map(tag => (
                              <Badge key={tag} variant="secondary" className="text-xs bg-gray-500/10 text-gray-400 border-gray-500/30">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        </motion.div>
                      ))
                    ) : (
                      <div className="col-span-full text-center py-12">
                        <div className="text-gray-400 text-lg mb-2">Aucune stratégie trouvée</div>
                        <div className="text-gray-500 text-sm">
                          Essayez de changer les filtres ou la recherche
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Configuration Panel - PLEINE LARGEUR EN DESSOUS */}
          <div>
            {!selectedStrategy ? (
              <Card className="bg-[#1a1a24] border-violet-500/20">
                <CardContent className="p-12 text-center">
                  <div className="flex flex-col items-center gap-4">
                    <div className="p-4 bg-violet-500/10 rounded-full">
                      <Target className="w-12 h-12 text-violet-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-white">Sélectionnez une stratégie</h3>
                    <p className="text-gray-400 max-w-md">
                      Choisissez une stratégie ci-dessus pour commencer la configuration de votre backtest
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="bg-[#1a1a24] border-violet-500/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-2xl text-white">
                    <Settings className="w-6 h-6 text-violet-400" />
                    Étape 2 : Configuration du Backtest
                  </CardTitle>
                  <p className="text-gray-400">
                    Configurez tous les paramètres de votre analyse en détail
                  </p>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Stratégie sélectionnée */}
                      <div className="bg-[#1a1a24] rounded-xl p-6 border border-violet-500/30 shadow-lg shadow-violet-500/10">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-3">
                              <div className="w-12 h-12 bg-violet-500/10 rounded-lg flex items-center justify-center border border-violet-500/20">
                                <span className="text-2xl">🎯</span>
                              </div>
                              <div>
                                <h3 className="text-xl font-bold text-white">
                                  {selectedStrategy.name}
                                </h3>
                                <p className="text-sm text-violet-400">
                                  Stratégie sélectionnée
                                </p>
                              </div>
                            </div>
                            <p className="text-gray-300 mb-4">
                              {selectedStrategy.description}
                            </p>
                            <div className="flex gap-3">
                              <Badge variant="secondary" className="bg-violet-500/10 text-violet-400 border border-violet-500/30">
                                📊 {selectedStrategy.timeframe}
                              </Badge>
                              <Badge variant="secondary" className="bg-violet-500/10 text-violet-400 border border-violet-500/30">
                                🎯 {selectedStrategy.risk_model}
                              </Badge>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedStrategy(null)}
                            className="text-violet-400 hover:text-violet-300 hover:bg-violet-500/10"
                          >
                            Changer
                          </Button>
                        </div>
                      </div>

                      {/* Nom du backtest */}
                      <div className="space-y-4 bg-[#1a1a24] rounded-xl p-6 border border-violet-500/20">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-violet-500/10 rounded-lg">
                            <span className="text-xl">📝</span>
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-white">Nom du Backtest</h3>
                            <p className="text-sm text-gray-400">Donnez un nom descriptif à votre analyse</p>
                          </div>
                        </div>
                        <input
                          type="text"
                          value={backtestName}
                          onChange={(e) => setBacktestName(e.target.value)}
                          placeholder="Ex: Test RSI modifié - Période Q4 2024"
                          className="w-full px-4 py-3 text-base bg-black/40 border border-violet-500/30 rounded-lg text-white placeholder:text-gray-500 focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all"
                        />
                        <p className="text-xs text-gray-500 flex items-center gap-2">
                          <span className="text-violet-400">💡</span> Un nom clair vous aidera à identifier facilement ce backtest
                        </p>
                      </div>

                      {/* Période des données */}
                      <div className="space-y-6 bg-[#1a1a24] rounded-xl p-6 border border-violet-500/20">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-violet-500/10 rounded-lg">
                              <Calendar className="h-5 w-5 text-violet-400" />
                            </div>
                            <div>
                              <h3 className="text-lg font-semibold text-white">Période des Données</h3>
                              <p className="text-sm text-gray-400">Choisissez la période d'analyse</p>
                            </div>
                          </div>
                          {periodType !== 'all' && (
                            <Badge variant="secondary" className="text-xs bg-violet-500/10 text-violet-400 border border-violet-500/30 font-mono">
                              {periodType === 'last_month' && `${getDateRange().start} → ${getDateRange().end}`}
                              {periodType === 'experimental' && `${getDateRange().start} → ${getDateRange().end}`}
                              {periodType === 'custom' && `${startDate} → ${endDate}`}
                            </Badge>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                          <button
                            onClick={() => setPeriodType('all')}
                            className={`p-4 text-left border rounded-lg transition-all ${
                              periodType === 'all' 
                                ? 'bg-violet-500/20 text-white border-violet-500 shadow-lg shadow-violet-500/20' 
                                : 'bg-black/40 text-gray-400 border-violet-500/20 hover:border-violet-500/50 hover:bg-violet-500/10'
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-xl">📊</span>
                              <div className="font-semibold text-sm">Toutes les Données</div>
                            </div>
                            <div className="text-xs opacity-70">
                              Fichier CSV complet
                            </div>
                          </button>
                          
                          <button
                            onClick={() => setPeriodType('last_month')}
                            className={`p-4 text-left border rounded-lg transition-all ${
                              periodType === 'last_month' 
                                ? 'bg-violet-500/20 text-white border-violet-500 shadow-lg shadow-violet-500/20' 
                                : 'bg-black/40 text-gray-400 border-violet-500/20 hover:border-violet-500/50 hover:bg-violet-500/10'
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-xl">📅</span>
                              <div className="font-semibold text-sm">Dernier Mois</div>
                            </div>
                            <div className="text-xs opacity-70">
                              30 derniers jours
                            </div>
                          </button>
                          
                          <button
                            onClick={() => setPeriodType('experimental')}
                            className={`p-4 text-left border rounded-lg transition-all ${
                              periodType === 'experimental' 
                                ? 'bg-violet-500/20 text-white border-violet-500 shadow-lg shadow-violet-500/20' 
                                : 'bg-black/40 text-gray-400 border-violet-500/20 hover:border-violet-500/50 hover:bg-violet-500/10'
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-xl">🧪</span>
                              <div className="font-semibold text-sm">Test Rapide</div>
                            </div>
                            <div className="text-xs opacity-70">
                              Dernière semaine
                            </div>
                          </button>
                          
                          <button
                            onClick={() => setPeriodType('custom')}
                            className={`p-4 text-left border rounded-lg transition-all ${
                              periodType === 'custom' 
                                ? 'bg-violet-500/20 text-white border-violet-500 shadow-lg shadow-violet-500/20' 
                                : 'bg-black/40 text-gray-400 border-violet-500/20 hover:border-violet-500/50 hover:bg-violet-500/10'
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-xl">⚙️</span>
                              <div className="font-semibold text-sm">Personnalisée</div>
                            </div>
                            <div className="text-xs opacity-70">
                              Dates précises
                            </div>
                          </button>
                        </div>

                        {periodType === 'custom' && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="bg-black/40 rounded-xl p-6 border-l-4 border-violet-500"
                          >
                            <h4 className="font-semibold mb-4 flex items-center gap-2 text-white">
                              <Calendar className="w-4 h-4 text-violet-400" />
                              Définir la période personnalisée
                            </h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                              <div>
                                <label className="text-sm font-medium text-gray-400 block mb-2">
                                  📅 Date de début
                                </label>
                                <input
                                  type="date"
                                  value={startDate}
                                  onChange={(e) => setStartDate(e.target.value)}
                                  className="w-full px-4 py-3 text-sm border border-violet-500/30 rounded-lg bg-black/40 text-white focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500"
                                />
                              </div>
                              <div>
                                <label className="text-sm font-medium text-gray-400 block mb-2">
                                  📅 Date de fin
                                </label>
                                <input
                                  type="date"
                                  value={endDate}
                                  onChange={(e) => setEndDate(e.target.value)}
                                  className="w-full px-4 py-3 text-sm border border-violet-500/30 rounded-lg bg-black/40 text-white focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500"
                                />
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </div>

                      {/* Paramètres avancés */}
                      <div className="space-y-4">
                        <Button
                          onClick={() => setShowAdvanced(!showAdvanced)}
                          variant="outline"
                          className="w-full justify-between p-4 h-auto bg-[#1a1a24] border-violet-500/20 hover:border-violet-500/50 hover:bg-violet-500/10 transition-all"
                          size="lg"
                        >
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-violet-500/10 rounded-lg">
                              <Settings className="h-5 w-5 text-violet-400" />
                            </div>
                            <div className="text-left">
                              <div className="font-semibold text-white">Paramètres Avancés</div>
                              <div className="text-sm text-gray-400">
                                Ajuster les paramètres spécifiques
                              </div>
                            </div>
                          </div>
                          <motion.div
                            animate={{ rotate: showAdvanced ? 180 : 0 }}
                            transition={{ duration: 0.2 }}
                            className="text-violet-400 text-xl"
                          >
                            ↓
                          </motion.div>
                        </Button>

                        {showAdvanced && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="bg-[#1a1a24] rounded-xl p-6 border border-violet-500/20"
                          >
                            <div className="flex items-center gap-3 mb-6">
                              <Settings className="h-5 w-5 text-violet-400" />
                              <h4 className="text-lg font-semibold text-white">Paramètres de {selectedStrategy.name}</h4>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-h-80 overflow-y-auto">
                              {Object.entries(parameters).map(([key, value]) => (
                                <div key={key} className="space-y-2">
                                  <label className="text-sm font-medium text-gray-400 block">
                                    {key}
                                  </label>
                                  <input
                                    type={typeof value === 'number' ? 'number' : 'text'}
                                    value={String(value)}
                                    onChange={(e) => {
                                      const newValue = typeof value === 'number' 
                                        ? parseFloat(e.target.value) || 0
                                        : e.target.value
                                      setParameters(prev => ({ ...prev, [key]: newValue }))
                                    }}
                                    step={typeof value === 'number' && value < 1 ? '0.01' : '1'}
                                    className="w-full px-3 py-2 text-sm border border-violet-500/30 rounded-md bg-black/40 text-white font-mono focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all"
                                  />
                                </div>
                              ))}
                            </div>
                          </motion.div>
                        )}
                      </div>

                      {/* Bouton de lancement */}
                      <div className="pt-6 border-t border-violet-500/20">
                        <Button
                          onClick={handleRun}
                          disabled={isCreatingRun}
                          className="w-full h-14 text-lg bg-gradient-to-r from-violet-500 to-violet-600 hover:from-violet-400 hover:to-violet-500 text-black font-bold shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50 border-0 transition-all disabled:opacity-50"
                          size="lg"
                        >
                          {isCreatingRun ? (
                            <>
                              <Loader2 className="mr-3 h-6 w-6 animate-spin" />
                              Lancement en cours...
                            </>
                          ) : (
                            <>
                              <Play className="mr-3 h-6 w-6 fill-black" />
                              Lancer le Backtest
                            </>
                          )}
                        </Button>
                      </div>
                </CardContent>
              </Card>
            )}

            {/* Statut du run */}
            {selectedStrategy && currentRunId && runStatus && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mt-6"
                >
                  <Card className="bg-[#1a1a24] border-violet-500/20">
                    <CardHeader>
                      <CardTitle className="text-xl flex items-center gap-2 text-white">
                        <Activity className="w-6 h-6 text-violet-400" />
                        Statut de l'Exécution
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div>
                        <p className="text-sm text-gray-400 mb-3">Run ID</p>
                        <code className="text-sm bg-black/40 border border-violet-500/30 text-violet-400 px-4 py-3 rounded-lg block break-all font-mono">
                          {currentRunId}
                        </code>
                      </div>

                      <div>
                        <p className="text-sm text-gray-400 mb-3">Statut</p>
                        <StatusBadge status={runStatus.status} message={runStatus.message} />
                      </div>

                      {runStatus.progress > 0 && (
                        <div>
                          <div className="flex justify-between text-sm mb-3">
                            <span className="text-gray-400">Progression</span>
                            <span className="font-medium text-violet-400">{Math.round(runStatus.progress * 100)}%</span>
                          </div>
                          <div className="h-4 bg-black/40 border border-violet-500/20 rounded-full overflow-hidden">
                            <motion.div
                              className="h-full bg-gradient-to-r from-violet-500 to-violet-600 shadow-lg shadow-violet-500/50"
                              initial={{ width: 0 }}
                              animate={{ width: `${runStatus.progress * 100}%` }}
                              transition={{ duration: 0.5 }}
                            />
                          </div>
                        </div>
                      )}

                      {runStatus.status === 'completed' && (
                        <Button
                          variant="outline"
                          className="w-full h-12 border-violet-500/50 text-violet-400 hover:bg-violet-500/10 hover:border-violet-400 hover:shadow-lg hover:shadow-violet-500/20 transition-all"
                          onClick={() => router.push(`/results/${currentRunId}`)}
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          Voir les Résultats Détaillés
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
