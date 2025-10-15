'use client'

import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { Strategy } from '@/types/api'

interface StrategyCardProps {
  strategy: Strategy
  onRun?: (strategy: Strategy) => void
  index?: number
}

export function StrategyCard({ strategy, onRun, index = 0 }: StrategyCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card className="h-full">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-xl">{strategy.name}</CardTitle>
              <CardDescription className="mt-2">
                {strategy.description}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Tags */}
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className="text-xs">
                📊 {strategy.timeframe}
              </Badge>
              <Badge variant="outline" className="text-xs">
                🎯 {strategy.risk_model}
              </Badge>
            </div>

            {/* Parameters */}
            {Object.keys(strategy.parameters).length > 0 && (
              <div>
                <p className="text-sm font-semibold mb-2">Paramètres configurables:</p>
                <div className="flex flex-wrap gap-2">
                  {Object.keys(strategy.parameters).slice(0, 3).map((key) => (
                    <code
                      key={key}
                      className="text-xs px-2 py-1 bg-muted rounded"
                    >
                      {key}
                    </code>
                  ))}
                  {Object.keys(strategy.parameters).length > 3 && (
                    <span className="text-xs text-muted-foreground">
                      +{Object.keys(strategy.parameters).length - 3} autres
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-2">
              <Button
                onClick={() => onRun?.(strategy)}
                className="flex-1"
                size="sm"
              >
                ▶️ Lancer
              </Button>
              <Button variant="outline" size="sm">
                📋 Détails
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
