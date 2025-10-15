/**
 * Client API pour communiquer avec le backend FastAPI
 */

import axios from 'axios'
import type {
  StrategyListResponse,
  Strategy,
  RunRequest,
  RunResponse,
  RunListResponse,
  RunStatus,
  RunResults
} from '@/types/api'

// Configuration axios
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30s timeout
})

// Intercepteur pour les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

/**
 * API des stratégies
 */
export const strategiesApi = {
  /**
   * Récupère la liste des stratégies disponibles
   */
  list: async (): Promise<StrategyListResponse> => {
    console.log('🔄 Appel API /strategies')
    const response = await api.get<StrategyListResponse>('/strategies')
    console.log('✅ Réponse API reçue:', response.data.strategies.length, 'stratégies')
    if (response.data.strategies.length > 0) {
      console.log('📋 Première stratégie:', response.data.strategies[0])
    }
    return response.data
  },

  /**
   * Récupère une stratégie par son ID
   */
  get: async (strategyId: string): Promise<Strategy> => {
    const response = await api.get<Strategy>(`/strategies/${strategyId}`)
    return response.data
  },
}

/**
 * API des runs
 */
export const runsApi = {
  /**
   * Lance un nouveau backtest
   */
  create: async (request: RunRequest): Promise<RunResponse> => {
    const response = await api.post<RunResponse>('/runs', request)
    return response.data
  },

  /**
   * Récupère la liste des runs
   */
  list: async (): Promise<RunListResponse> => {
    const response = await api.get<RunListResponse>('/runs')
    return response.data
  },

  /**
   * Récupère le statut d'un run
   */
  getStatus: async (runId: string): Promise<RunStatus> => {
    const response = await api.get<RunStatus>(`/runs/${runId}/status`)
    return response.data
  },

  /**
   * Récupère les résultats d'un run terminé
   */
  getResults: async (runId: string): Promise<RunResults> => {
    const response = await api.get<RunResults>(`/runs/${runId}/results`)
    return response.data
  },

  /**
   * Supprime un run
   */
  delete: async (runId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete<{ success: boolean; message: string }>(`/runs/${runId}`)
    return response.data
  },
}

/**
 * API de santé
 */
export const healthApi = {
  /**
   * Vérifie la santé du backend
   */
  check: async (): Promise<{ status: string }> => {
    const response = await api.get('/')
    return response.data
  },
}
