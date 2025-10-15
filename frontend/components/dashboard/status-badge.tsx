'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'

interface StatusBadgeProps {
  status: 'running' | 'completed' | 'failed'
  message?: string
}

export function StatusBadge({ status, message }: StatusBadgeProps) {
  const config = {
    running: {
      variant: 'warning' as const,
      icon: '⚡',
      label: 'EN COURS',
      pulse: true,
    },
    completed: {
      variant: 'success' as const,
      icon: '✅',
      label: 'TERMINÉ',
      pulse: false,
    },
    failed: {
      variant: 'destructive' as const,
      icon: '❌',
      label: 'ÉCHEC',
      pulse: false,
    },
  }

  const { variant, icon, label, pulse } = config[status]

  return (
    <Badge variant={variant} className="flex items-center gap-2">
      {pulse ? (
        <motion.span
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          {icon}
        </motion.span>
      ) : (
        <span>{icon}</span>
      )}
      <span className="font-semibold">{label}</span>
      {message && (
        <span className="font-normal ml-2 opacity-80">{message}</span>
      )}
    </Badge>
  )
}
