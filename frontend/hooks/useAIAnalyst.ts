import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ChatRequest {
  message: string
  context?: Record<string, any>
  run_id?: string
}

interface ChatResponse {
  response: string
  metadata?: Record<string, any>
}

interface Run {
  run_id: string
  strategy: string
  timestamp: string
  status: 'completed' | 'incomplete'
}

// Hook pour envoyer des messages au chat
export function useSendMessage() {
  return useMutation<ChatResponse, Error, ChatRequest>({
    mutationFn: async (data) => {
      const response = await axios.post(`${API_URL}/api/ai/chat`, data)
      return response.data
    },
  })
}

// Hook pour récupérer les runs disponibles
export function useAvailableRuns() {
  return useQuery<{ runs: Run[] }>({
    queryKey: ['ai-runs'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/ai/runs`)
      return response.data
    },
    staleTime: 30000, // 30 seconds
  })
}

// Hook pour récupérer le résumé d'un run
export function useRunSummary(runId: string | null) {
  return useQuery<{ run_id: string; summary: string }>({
    queryKey: ['run-summary', runId],
    queryFn: async () => {
      if (!runId) throw new Error('No run ID provided')
      const response = await axios.get(`${API_URL}/api/ai/run/${runId}/summary`)
      return response.data
    },
    enabled: !!runId,
  })
}
