'use client'

import { useMemo } from 'react'
import {
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Bar,
  Line
} from 'recharts'

interface OHLCBar {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface OHLCChartProps {
  data: OHLCBar[]
  symbol: string
}

// Composant personnalisé pour les bougies OHLC
const CandlestickBar = (props: any) => {
  const { payload, x, y, width, height } = props
  
  if (!payload) return null
  
  const { open, high, low, close } = payload
  const isGreen = close >= open
  const color = isGreen ? '#00ff88' : '#ff4757'
  const fillColor = isGreen ? '#00ff88' : '#ff4757'
  
  // Calculer les positions
  const bodyTop = Math.max(open, close)
  const bodyBottom = Math.min(open, close)
  const bodyHeight = Math.abs(close - open)
  
  // Échelle des prix (approximative)
  const priceRange = high - low
  const pixelPerPoint = height / priceRange
  
  const wickTop = y + (high - Math.max(open, close)) * pixelPerPoint
  const wickBottom = y + height - (Math.min(open, close) - low) * pixelPerPoint
  const bodyY = y + (high - bodyTop) * pixelPerPoint
  const bodyHeightPx = bodyHeight * pixelPerPoint
  
  return (
    <g>
      {/* Mèche haute */}
      <line
        x1={x + width / 2}
        y1={wickTop}
        x2={x + width / 2}
        y2={bodyY}
        stroke={color}
        strokeWidth={1}
      />
      {/* Mèche basse */}
      <line
        x1={x + width / 2}
        y1={bodyY + bodyHeightPx}
        x2={x + width / 2}
        y2={wickBottom}
        stroke={color}
        strokeWidth={1}
      />
      {/* Corps de la bougie */}
      <rect
        x={x + width * 0.2}
        y={bodyY}
        width={width * 0.6}
        height={Math.max(bodyHeightPx, 1)}
        fill={isGreen ? 'transparent' : fillColor}
        stroke={color}
        strokeWidth={1}
      />
    </g>
  )
}

export function OHLCChart({ data, symbol }: OHLCChartProps) {
  const chartData = useMemo(() => {
    return data.map((bar, index) => ({
      ...bar,
      index,
      time: new Date(bar.timestamp).toLocaleString('fr-FR', {
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }),
      color: bar.close >= bar.open ? '#00ff88' : '#ff4757'
    }))
  }, [data])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      const isGreen = data.close >= data.open
      
      return (
        <div className="bg-[#1a1a24] border border-violet-500/30 rounded-lg p-4 shadow-lg">
          <p className="text-white font-semibold mb-2">{label}</p>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-gray-400">Open:</span>
              <span className="text-white font-mono">{data.open.toFixed(2)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-gray-400">High:</span>
              <span className="text-white font-mono">{data.high.toFixed(2)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-gray-400">Low:</span>
              <span className="text-white font-mono">{data.low.toFixed(2)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-gray-400">Close:</span>
              <span className={`font-mono ${isGreen ? 'text-[#00ff88]' : 'text-[#ff4757]'}`}>
                {data.close.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-gray-400">Volume:</span>
              <span className="text-white font-mono">{data.volume.toLocaleString()}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-gray-400">Change:</span>
              <span className={`font-mono ${isGreen ? 'text-[#00ff88]' : 'text-[#ff4757]'}`}>
                {isGreen ? '+' : ''}{(data.close - data.open).toFixed(2)} 
                ({((data.close - data.open) / data.open * 100).toFixed(2)}%)
              </span>
            </div>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-[600px]">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#374151" 
            opacity={0.3}
          />
          <XAxis 
            dataKey="time"
            stroke="#9CA3AF"
            fontSize={12}
            interval="preserveStartEnd"
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            stroke="#9CA3AF"
            fontSize={12}
            domain={['dataMin - 10', 'dataMax + 10']}
            tickFormatter={(value) => value.toFixed(0)}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Barres OHLC personnalisées */}
          <Bar 
            dataKey="high" 
            shape={<CandlestickBar />}
            fill="transparent"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
