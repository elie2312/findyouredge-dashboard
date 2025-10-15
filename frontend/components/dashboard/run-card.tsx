'use client'

import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StatusBadge } from './status-badge'
import { formatDate, formatDuration } from '@/lib/utils'
import type { RunInfo } from '@/types/api'

interface RunCardProps {
  run: RunInfo
  onViewResults?: (runId: string) => void
  index?: number
}

export function RunCard({ run, onViewResults, index = 0 }: RunCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
    >
      <Card>
        <CardContent className="p-4">
          <div className="space-y-3">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <p className="font-mono text-sm font-semibold">
                  {run.run_id.slice(0, 20)}...
                </p>
                {run.started_at && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatDate(run.started_at)}
                  </p>
                )}
              </div>
              <StatusBadge status={run.status} />
            </div>

            {/* Message */}
            <p className="text-sm text-muted-foreground">{run.message}</p>

            {/* Duration */}
            {run.duration_seconds && (
              <p className="text-xs text-muted-foreground">
                ⏱️ Durée: {formatDuration(run.duration_seconds)}
              </p>
            )}

            {/* Actions */}
            {run.status === 'completed' && onViewResults && (
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => onViewResults(run.run_id)}
              >
                📊 Voir les résultats
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
