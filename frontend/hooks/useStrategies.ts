/**
 * Hooks pour les stratégies
 */

import { useQuery } from '@tanstack/react-query'
import { strategiesApi } from '@/lib/api'

/**
 * Hook pour récupérer la liste des stratégies
 */
export function useStrategies() {
  return useQuery({
    queryKey: ['strategies'],
    queryFn: strategiesApi.list,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
  })
}

/**
 * Hook pour récupérer une stratégie par son ID
 */
export function useStrategy(strategyId: string) {
  return useQuery({
    queryKey: ['strategies', strategyId],
    queryFn: () => strategiesApi.get(strategyId),
    enabled: !!strategyId,
    staleTime: 5 * 60 * 1000,
  })
}
