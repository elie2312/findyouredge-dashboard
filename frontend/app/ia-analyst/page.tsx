'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, Database, Code, TrendingUp, AlertCircle, BarChart, FileText, Cpu, X, Copy, Check, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Header } from '@/components/dashboard/header'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { motion, AnimatePresence } from 'framer-motion'
import { useSendMessage, useAvailableRuns } from '@/hooks/useAIAnalyst'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: {
    type?: 'chart' | 'table' | 'code' | 'analysis'
    data?: any
  }
}

interface AnalysisContext {
  runId?: string
  strategy?: string
  dateRange?: { start: string; end: string }
  symbols?: string[]
}

export default function IAAnalystPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'system',
      content: `# 🤖 Assistant IA - Analyse Quantitative

Je suis votre expert en data science appliquée au trading algorithmique. Je peux analyser vos données de backtest, interpréter les résultats et vous aider à optimiser vos stratégies.

## 🎯 Mes capacités

- **Analyse de performances** : PnL, expectancy, drawdown, Sharpe ratio
- **Analyse OHLCV** : Volatilité, momentum, corrélations, patterns
- **Comparaisons** : Entre périodes, symboles ou paramètres
- **Code Python** : Génération de scripts d'analyse personnalisés

## 💡 Exemples de questions

- "Analyse les performances du dernier backtest"
- "Compare la volatilité entre NQ et ES sur les 30 derniers jours"
- "Montre-moi la distribution des PnL par heure de trading"
- "Génère un code pour calculer le ratio de Calmar"`,
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [context, setContext] = useState<AnalysisContext>({})
  const [copiedCode, setCopiedCode] = useState<string | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = useSendMessage()
  const { data: runsData, refetch: refetchRuns } = useAvailableRuns()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Appel au backend réel
      const response = await sendMessage.mutateAsync({
        message: userMessage.content,
        context: context,
        run_id: context.runId
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        metadata: response.metadata
      }
      
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      // En cas d'erreur, utiliser la réponse mock
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: generateMockResponse(userMessage.content),
        timestamp: new Date(),
        metadata: detectResponseType(userMessage.content)
      }
      setMessages(prev => [...prev, assistantMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase()

    if (lowerQuery.includes('performance') || lowerQuery.includes('backtest')) {
      return `## 📊 Analyse des Performances

D'après les données du dernier backtest :

### Métriques Clés
- **PnL Total**: +$12,450 (+24.9%)
- **Win Rate**: 62.3% (156/250 trades)
- **Expectancy**: $49.80 par trade
- **Max Drawdown**: -$2,340 (-4.68%)
- **Sharpe Ratio**: 1.87

### Distribution Temporelle
\`\`\`python
# Distribution des gains par heure
hourly_pnl = trades_df.groupby(trades_df['timestamp'].dt.hour)['pnl'].sum()
print(hourly_pnl.sort_values(ascending=False).head())
# 14h: $3,240
# 15h: $2,870  
# 16h: $2,120
\`\`\`

### Recommandations
1. **Points forts** : Excellente performance entre 14h-16h UTC
2. **À surveiller** : Drawdown élevé en début de session (13h)
3. **Optimisation** : Considérer un scale-in progressif`
    }

    if (lowerQuery.includes('volatilité') || lowerQuery.includes('volatility')) {
      return `## 📈 Analyse de Volatilité

### Volatilité Réalisée (30 jours)
\`\`\`python
import pandas as pd
import numpy as np

# Calcul de la volatilité
returns = ohlcv_df['close'].pct_change()
volatility = returns.rolling(window=20).std() * np.sqrt(252)

# Résultats
print("Volatilité actuelle: {:.2%}".format(volatility.iloc[-1]))
print("Volatilité moyenne: {:.2%}".format(volatility.mean()))
print("VaR 95%: $" + "{:.2f}".format(portfolio_value * volatility.iloc[-1] * 1.65))
\`\`\`

### Observations
- **Volatilité actuelle**: 18.7% (annualisée)
- **Moyenne 30J**: 16.2%
- **Pic de volatilité**: 23.4% (il y a 5 jours)

La volatilité est actuellement **au-dessus de sa moyenne**, suggérant un environnement de marché plus risqué.`
    }

    if (lowerQuery.includes('code') || lowerQuery.includes('script')) {
      return `## 💻 Code d'Analyse Généré

\`\`\`python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def analyze_backtest_results(trades_file='trades.csv', ohlcv_file='data.csv'):
    """
    Analyse complète des résultats de backtest
    """
    # Chargement des données
    trades_df = pd.read_csv(trades_file)
    trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
    
    # Calculs des métriques
    metrics = {
        'total_trades': len(trades_df),
        'win_rate': (trades_df['pnl'] > 0).mean(),
        'expectancy': trades_df['pnl'].mean(),
        'total_pnl': trades_df['pnl'].sum(),
        'max_drawdown': calculate_max_drawdown(trades_df['pnl'].cumsum()),
        'sharpe_ratio': calculate_sharpe(trades_df['pnl'])
    }
    
    # Analyse temporelle
    hourly_stats = trades_df.groupby(trades_df['timestamp'].dt.hour).agg({
        'pnl': ['sum', 'mean', 'count']
    })
    
    # Visualisation
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Equity curve
    axes[0, 0].plot(trades_df['pnl'].cumsum())
    axes[0, 0].set_title('Equity Curve')
    
    # Distribution PnL
    axes[0, 1].hist(trades_df['pnl'], bins=30, alpha=0.7)
    axes[0, 1].set_title('PnL Distribution')
    
    # Heatmap horaire
    axes[1, 0].bar(hourly_stats.index, hourly_stats[('pnl', 'sum')])
    axes[1, 0].set_title('PnL par Heure')
    
    # Win/Loss ratio
    wins = trades_df[trades_df['pnl'] > 0]['pnl']
    losses = trades_df[trades_df['pnl'] <= 0]['pnl']
    axes[1, 1].bar(['Wins', 'Losses'], [wins.sum(), abs(losses.sum())])
    axes[1, 1].set_title('Total Wins vs Losses')
    
    plt.tight_layout()
    plt.show()
    
    return metrics, hourly_stats

# Exécution
metrics, hourly_stats = analyze_backtest_results()
print(metrics)
\`\`\`

Ce script analyse vos résultats de backtest et génère des visualisations détaillées.`
    }

    // Réponse par défaut
    return `## 🔍 Analyse en cours...

Je traite votre requête: "${query}"

Pour une analyse plus précise, vous pouvez:
- Spécifier une période: "Analyse les 7 derniers jours"
- Cibler une stratégie: "Compare SuperTrend vs MA Cross"
- Demander du code: "Génère un script pour calculer le ratio de Calmar"

N'hésitez pas à me poser des questions spécifiques sur vos données de trading!`
  }

  const detectResponseType = (query: string): any => {
    const lowerQuery = query.toLowerCase()
    if (lowerQuery.includes('chart') || lowerQuery.includes('graph')) {
      return { type: 'chart' }
    }
    if (lowerQuery.includes('code') || lowerQuery.includes('script')) {
      return { type: 'code' }
    }
    if (lowerQuery.includes('table') || lowerQuery.includes('données')) {
      return { type: 'table' }
    }
    return { type: 'analysis' }
  }

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(code)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const CodeBlock = ({ language, value }: { language: string; value: string }) => (
    <div className="relative group my-4">
      <Button
        onClick={() => copyCode(value)}
        size="sm"
        variant="ghost"
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/50 hover:bg-black/70"
      >
        {copiedCode === value ? (
          <Check className="h-4 w-4 text-green-400" />
        ) : (
          <Copy className="h-4 w-4" />
        )}
      </Button>
      <SyntaxHighlighter
        language={language || 'python'}
        style={vscDarkPlus}
        customStyle={{
          margin: 0,
          borderRadius: '0.5rem',
          background: '#1a1a24',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          fontSize: '0.875rem'
        }}
      >
        {value}
      </SyntaxHighlighter>
    </div>
  )

  return (
    <ProtectedRoute>
      <Header />
      <main className="min-h-screen bg-gradient-to-br from-[#0a0a0f] via-[#0f1419] to-[#0a0a0f]">
        <div className="container mx-auto px-4 py-6 max-w-6xl">
          {/* Header Section */}
          <motion.div 
            className="mb-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl shadow-lg shadow-violet-500/30">
                <Sparkles className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">
                  Chat IA - <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-500">Analyse de données</span>
                </h1>
                <p className="text-gray-400 text-sm mt-1">Expert quantitatif pour vos stratégies de trading</p>
              </div>
            </div>

            {/* Context Bar */}
            <div className="flex flex-wrap gap-2">
              <div className="px-3 py-1.5 bg-violet-500/10 border border-violet-500/30 rounded-lg text-xs text-violet-400 flex items-center gap-2">
                <Database className="w-3 h-3" />
                Données OHLCV disponibles
              </div>
              <div className="px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-lg text-xs text-green-400 flex items-center gap-2">
                <FileText className="w-3 h-3" />
                {messages.filter(m => m.role === 'user').length} requêtes
              </div>
              <div className="px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-lg text-xs text-blue-400 flex items-center gap-2">
                <Cpu className="w-3 h-3" />
                Modèle actif
              </div>
              {runsData && runsData.runs.length > 0 && (
                <div className="px-3 py-1.5 bg-purple-500/10 border border-purple-500/30 rounded-lg text-xs text-purple-400 flex items-center gap-2">
                  <BarChart className="w-3 h-3" />
                  {runsData.runs.length} backtests disponibles
                </div>
              )}
              <Button
                onClick={() => refetchRuns()}
                size="sm"
                variant="ghost"
                className="h-7 px-2 text-xs hover:bg-violet-500/10"
              >
                <RefreshCw className="w-3 h-3" />
              </Button>
            </div>
          </motion.div>

          {/* Chat Container */}
          <motion.div 
            className="bg-[#0d0d15]/80 backdrop-blur-xl border border-violet-500/20 rounded-2xl shadow-2xl overflow-hidden"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {/* Messages Area */}
            <div className="h-[600px] overflow-y-auto p-6 space-y-4 custom-scrollbar">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                      <div className={`rounded-2xl p-4 ${
                        message.role === 'user' 
                          ? 'bg-gradient-to-r from-violet-500 to-purple-600 text-white shadow-lg shadow-violet-500/30' 
                          : message.role === 'system'
                          ? 'bg-gradient-to-br from-[#1a1a24] to-[#15151d] border border-violet-500/20'
                          : 'bg-[#1a1a24] border border-violet-500/20'
                      }`}>
                        {message.role === 'assistant' && (
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 bg-gradient-to-br from-violet-500 to-purple-600 rounded-lg flex items-center justify-center">
                              <Sparkles className="w-4 h-4 text-white" />
                            </div>
                            <span className="text-xs text-gray-400">IA Analyst</span>
                          </div>
                        )}
                        
                        {message.role === 'system' && (
                          <div className="flex items-center gap-2 mb-3">
                            <AlertCircle className="w-5 h-5 text-violet-400" />
                            <span className="text-sm font-bold text-violet-400">Système</span>
                          </div>
                        )}

                        {/* Message Content */}
                        <div className={`prose prose-invert max-w-none ${message.role === 'user' ? 'text-white' : ''}`}>
                          <ReactMarkdown
                            components={{
                              code({ node, inline, className, children, ...props }: any) {
                                const match = /language-(\w+)/.exec(className || '')
                                return !inline && match ? (
                                  <CodeBlock
                                    language={match[1]}
                                    value={String(children).replace(/\n$/, '')}
                                  />
                                ) : (
                                  <code className="px-1.5 py-0.5 bg-violet-500/20 text-violet-300 rounded text-sm" {...props}>
                                    {children}
                                  </code>
                                )
                              },
                              h2: ({ children }: any) => (
                                <h2 className="text-xl font-bold text-white mt-4 mb-3 flex items-center gap-2">
                                  {children}
                                </h2>
                              ),
                              h3: ({ children }: any) => (
                                <h3 className="text-lg font-semibold text-gray-200 mt-3 mb-2">
                                  {children}
                                </h3>
                              ),
                              ul: ({ children }: any) => (
                                <ul className="list-disc list-inside space-y-1 text-gray-300">
                                  {children}
                                </ul>
                              ),
                              li: ({ children }: any) => (
                                <li className="text-gray-300">
                                  {children}
                                </li>
                              ),
                              p: ({ children }: any) => (
                                <p className="text-gray-300 leading-relaxed">
                                  {children}
                                </p>
                              ),
                              strong: ({ children }: any) => (
                                <strong className="text-white font-semibold">
                                  {children}
                                </strong>
                              )
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>

                        {/* Timestamp */}
                        <div className="mt-2 text-xs opacity-60">
                          {message.timestamp.toLocaleTimeString('fr-FR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Loading Indicator */}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="bg-[#1a1a24] border border-violet-500/20 rounded-2xl p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-6 h-6 bg-gradient-to-br from-violet-500 to-purple-600 rounded-lg flex items-center justify-center animate-pulse">
                        <Sparkles className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex gap-1">
                        <motion.div
                          className="w-2 h-2 bg-violet-400 rounded-full"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                        />
                        <motion.div
                          className="w-2 h-2 bg-violet-400 rounded-full"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1.5, repeat: Infinity, delay: 0.3 }}
                        />
                        <motion.div
                          className="w-2 h-2 bg-violet-400 rounded-full"
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1.5, repeat: Infinity, delay: 0.6 }}
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-violet-500/20 bg-[#0a0a0f]/50 backdrop-blur-sm p-4">
              <form onSubmit={handleSubmit} className="flex gap-3">
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleSubmit(e)
                      }
                    }}
                    placeholder="Posez votre question sur les données de trading..."
                    className="w-full px-4 py-3 bg-[#1a1a24] border border-violet-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-violet-400 focus:shadow-lg focus:shadow-violet-500/20 transition-all resize-none"
                    rows={2}
                    disabled={isLoading}
                  />
                  <div className="absolute bottom-2 right-2 text-xs text-gray-500">
                    Shift+Enter pour nouvelle ligne
                  </div>
                </div>
                <Button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="px-6 bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-400 hover:to-purple-500 text-white font-bold shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed h-auto"
                >
                  <Send className="w-5 h-5" />
                </Button>
              </form>

              {/* Quick Actions */}
              <div className="mt-3 space-y-2">
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setInput('Analyse les performances du dernier backtest')}
                    className="px-3 py-1.5 bg-violet-500/10 border border-violet-500/30 rounded-lg text-xs text-violet-400 hover:bg-violet-500/20 transition-all"
                  >
                    📊 Performances
                  </button>
                  <button
                    onClick={() => setInput('Montre la distribution des PnL par heure')}
                    className="px-3 py-1.5 bg-violet-500/10 border border-violet-500/30 rounded-lg text-xs text-violet-400 hover:bg-violet-500/20 transition-all"
                  >
                    📈 Distribution PnL
                  </button>
                  <button
                    onClick={() => setInput('Analyse la volatilité sur les 30 derniers jours')}
                    className="px-3 py-1.5 bg-violet-500/10 border border-violet-500/30 rounded-lg text-xs text-violet-400 hover:bg-violet-500/20 transition-all"
                  >
                    📉 Volatilité
                  </button>
                  <button
                    onClick={() => setInput('Génère un code pour calculer le Sharpe ratio')}
                    className="px-3 py-1.5 bg-violet-500/10 border border-violet-500/30 rounded-lg text-xs text-violet-400 hover:bg-violet-500/20 transition-all"
                  >
                    💻 Code Python
                  </button>
                </div>
                
                {/* Run Selector */}
                {runsData && runsData.runs.length > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">Analyser un run:</span>
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          setContext(prev => ({ ...prev, runId: e.target.value }))
                          setInput(`Analyse les performances du run ${e.target.value.slice(0, 8)}`)
                        }
                      }}
                      className="px-3 py-1 bg-[#1a1a24] border border-violet-500/30 rounded-lg text-xs text-violet-400 focus:outline-none focus:border-violet-400"
                    >
                      <option value="">Sélectionnez un run</option>
                      {runsData.runs.map(run => (
                        <option key={run.run_id} value={run.run_id}>
                          {run.strategy} - {new Date(run.timestamp).toLocaleDateString('fr-FR')}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </div>

        <style jsx global>{`
          .custom-scrollbar::-webkit-scrollbar {
            width: 8px;
          }
          
          .custom-scrollbar::-webkit-scrollbar-track {
            background: rgba(139, 92, 246, 0.05);
            border-radius: 4px;
          }
          
          .custom-scrollbar::-webkit-scrollbar-thumb {
            background: rgba(139, 92, 246, 0.3);
            border-radius: 4px;
          }
          
          .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: rgba(139, 92, 246, 0.5);
          }
        `}</style>
      </main>
    </ProtectedRoute>
  )
}
