'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useOHLCData } from '@/hooks/useOHLCData'
import { OHLCChart } from '@/components/charts/OHLCChart'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Header } from '@/components/dashboard/header'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { TrendingUp, Calendar, BarChart3, Loader2, RefreshCw } from 'lucide-react'

export default function ChartPage() {
  const [selectedDays, setSelectedDays] = useState(7)
  const { data: ohlcData, isLoading, error, refetch } = useOHLCData(selectedDays)

  const dayOptions = [
    { value: 1, label: '1 jour' },
    { value: 3, label: '3 jours' },
    { value: 7, label: '1 semaine' },
    { value: 14, label: '2 semaines' },
    { value: 30, label: '1 mois' }
  ]

  return (
    <ProtectedRoute>
      <Header />
      <div className="min-h-screen">
        <div className="container mx-auto px-6 py-12">
          {/* En-tête */}
          <div className="mb-12 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/10 border border-violet-500/30 text-violet-400 rounded-full text-sm font-bold tracking-wider mb-6">
              <BarChart3 className="w-4 h-4" />
              Analyse Graphique
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              <span className="text-violet-400">Graphique</span> OHLC
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Visualisation des données de prix en chandelier japonais (30 minutes)
            </p>
          </div>

          {/* Contrôles */}
          <Card className="mb-8 bg-[#1a1a24] border-violet-500/20">
            <CardHeader>
              <CardTitle className="text-xl text-white flex items-center gap-2">
                <Calendar className="w-6 h-6 text-violet-400" />
                Période d'affichage
              </CardTitle>
              <CardDescription>
                Sélectionnez la période à afficher sur le graphique
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                {dayOptions.map((option) => (
                  <Button
                    key={option.value}
                    variant={selectedDays === option.value ? "default" : "outline"}
                    onClick={() => setSelectedDays(option.value)}
                    className={
                      selectedDays === option.value
                        ? "bg-violet-500 hover:bg-violet-600 text-white border-violet-500"
                        : "bg-transparent border-violet-500/30 text-violet-400 hover:bg-violet-500/10 hover:border-violet-500/50"
                    }
                  >
                    {option.label}
                  </Button>
                ))}
                <Button
                  variant="outline"
                  onClick={() => refetch()}
                  disabled={isLoading}
                  className="bg-transparent border-violet-500/30 text-violet-400 hover:bg-violet-500/10 hover:border-violet-500/50"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4" />
                  )}
                  Actualiser
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Informations sur les données */}
          {ohlcData && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <Card className="bg-[#1a1a24] border-violet-500/20">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-violet-400" />
                    <div>
                      <p className="text-sm text-gray-400">Symbole</p>
                      <p className="text-lg font-bold text-white">{ohlcData.symbol}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-[#1a1a24] border-violet-500/20">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-violet-400" />
                    <div>
                      <p className="text-sm text-gray-400">Timeframe</p>
                      <p className="text-lg font-bold text-white">{ohlcData.timeframe}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-[#1a1a24] border-violet-500/20">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-violet-400" />
                    <div>
                      <p className="text-sm text-gray-400">Période</p>
                      <p className="text-lg font-bold text-white">{ohlcData.period}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-[#1a1a24] border-violet-500/20">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-violet-400" />
                    <div>
                      <p className="text-sm text-gray-400">Barres</p>
                      <p className="text-lg font-bold text-white">{ohlcData.total_bars}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Graphique principal */}
          <Card className="bg-[#1a1a24] border-violet-500/20">
            <CardHeader>
              <CardTitle className="text-2xl text-white flex items-center gap-2">
                <BarChart3 className="w-6 h-6 text-violet-400" />
                Graphique OHLC - {ohlcData?.symbol || 'NQ'} (30min)
              </CardTitle>
              <CardDescription>
                Chandelier japonais avec volumes - Dernière semaine de données
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center h-[600px]">
                  <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-violet-400 mx-auto mb-4" />
                    <p className="text-gray-400 mb-2">Chargement des données OHLC...</p>
                    <p className="text-sm text-gray-500">
                      📊 Lecture de {selectedDays} jour{selectedDays > 1 ? 's' : ''} de données (1.5GB)
                    </p>
                    <p className="text-xs text-gray-600 mt-2">
                      ⏱️ Premier chargement ~40s, puis cache instantané
                    </p>
                  </div>
                </div>
              ) : error ? (
                <div className="flex items-center justify-center h-[600px]">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl">⚠️</span>
                    </div>
                    <p className="text-red-400 mb-2">Erreur lors du chargement</p>
                    <p className="text-gray-400 text-sm">{error.message}</p>
                    <Button
                      onClick={() => refetch()}
                      className="mt-4 bg-violet-500 hover:bg-violet-600"
                    >
                      Réessayer
                    </Button>
                  </div>
                </div>
              ) : ohlcData && ohlcData.data.length > 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <OHLCChart data={ohlcData.data} symbol={ohlcData.symbol} />
                </motion.div>
              ) : (
                <div className="flex items-center justify-center h-[600px]">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-violet-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <BarChart3 className="w-6 h-6 text-violet-400" />
                    </div>
                    <p className="text-gray-400">Aucune donnée disponible pour cette période</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Légende */}
          <Card className="mt-8 bg-[#1a1a24] border-violet-500/20">
            <CardHeader>
              <CardTitle className="text-lg text-white">Légende</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-6 border border-[#00ff88] bg-transparent"></div>
                  <span className="text-gray-300">Bougie haussière (Close &gt; Open)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-4 h-6 border border-[#ff4757] bg-[#ff4757]"></div>
                  <span className="text-gray-300">Bougie baissière (Close &lt; Open)</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  )
}
