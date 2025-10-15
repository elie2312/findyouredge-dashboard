/**
 * Hooks pour les runs de backtest
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { runsApi } from '@/lib/api'
import type { RunRequest } from '@/types/api'

/**
 * Hook pour récupérer la liste des runs
 */
export function useRuns() {
  return useQuery({
    queryKey: ['runs'],
    queryFn: runsApi.list,
    refetchInterval: 5000, // Poll toutes les 5 secondes
    retry: 3,
  })
}

/**
 * Hook pour récupérer le statut d'un run
 */
export function useRunStatus(runId: string) {
  return useQuery({
    queryKey: ['runs', runId, 'status'],
    queryFn: () => runsApi.getStatus(runId),
    enabled: !!runId,
    refetchInterval: (query) => {
      // Poll plus fréquemment si le run est en cours
      return query.state.data?.status === 'running' ? 2000 : 10000
    },
    retry: 3,
  })
}

/**
 * Hook pour récupérer les résultats d'un run
 */
export function useRunResults(runId: string) {
  return useQuery({
    queryKey: ['runs', runId, 'results'],
    queryFn: () => runsApi.getResults(runId),
    enabled: !!runId,
    staleTime: 0, // Pas de cache - force refresh
    retry: 3,
  })
}

/**
 * Hook pour créer un nouveau run
 */
export function useCreateRun() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (request: RunRequest) => runsApi.create(request),
    onSuccess: () => {
      // Invalider la liste des runs pour la rafraîchir
      queryClient.invalidateQueries({ queryKey: ['runs'] })
    },
  })
}

/**
 * Hook pour supprimer un run
 */
export function useDeleteRun() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (runId: string) => runsApi.delete(runId),
    onSuccess: () => {
      // Invalider la liste des runs pour la rafraîchir
      queryClient.invalidateQueries({ queryKey: ['runs'] })
    },
  })
}
