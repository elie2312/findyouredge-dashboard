'use client'

import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface WinLossPieProps {
  winningTrades: number
  losingTrades: number
  title?: string
}

export function WinLossPie({ winningTrades, losingTrades, title = 'Répartition Win/Loss' }: WinLossPieProps) {
  const data = [
    { name: 'Trades Gagnants', value: winningTrades, color: '#10B981' },
    { name: 'Trades Perdants', value: losingTrades, color: '#EF4444' },
  ]

  const total = winningTrades + losingTrades
  const winRate = total > 0 ? (winningTrades / total * 100).toFixed(1) : '0'

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, delay: 0.3, ease: 'easeOut' }}
    >
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
                animationBegin={0}
                animationDuration={800}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
          
          {/* Win Rate au centre */}
          <div className="text-center mt-4">
            <p className="text-3xl font-bold text-primary">{winRate}%</p>
            <p className="text-sm text-muted-foreground">Win Rate</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
