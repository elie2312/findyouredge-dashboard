import { useQuery } from '@tanstack/react-query'
import { API_URL } from '@/lib/config'

interface OHLCBar {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface OHLCData {
  data: OHLCBar[]
  symbol: string
  timeframe: string
  period: string
  total_bars: number
}

export function useOHLCData(days: number = 7) {
  return useQuery<OHLCData>({
    queryKey: ['ohlc-data', days],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/api/runs/ohlc-data?days=${days}`)
      if (!response.ok) {
        throw new Error('Failed to fetch OHLC data')
      }
      return response.json()
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1
  })
}
