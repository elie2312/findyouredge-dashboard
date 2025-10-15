/**
 * Types pour l'API Backend
 */

export interface Strategy {
  id: string
  name: string
  description: string
  timeframe: string
  risk_model: string
  parameters: Record<string, any>
  script_path: string
  category: string
  tags: string[]
}

export interface StrategyListResponse {
  strategies: Strategy[]
}

export interface RunRequest {
  strategy_id: string
  parameters?: Record<string, any>
  name?: string
}

export interface RunResponse {
  run_id: string
  status: string
  message: string
  name?: string
  started_at?: string
}

export interface RunStatus {
  run_id: string
  status: 'running' | 'completed' | 'failed'
  progress: number
  message: string
  name?: string
  logs: string[]
  started_at?: string
  completed_at?: string
}

export interface RunInfo {
  run_id: string
  status: 'running' | 'completed' | 'failed'
  message: string
  name?: string
  started_at?: string
  completed_at?: string
  duration_seconds?: number
}

export interface RunListResponse {
  runs: RunInfo[]
  total: number
}

export interface RunMetrics {
  total_trades: number
  win_rate: number
  net_pnl: number
  profit_factor: number
  max_drawdown: number
  avg_win: number
  avg_loss: number
  expectancy: number
  winning_trades: number
  losing_trades: number
  gross_profit: number
  gross_loss: number
}

export interface Trade {
  id: number
  date: string
  entry_time: string
  exit_time: string
  direction: string
  entry: number
  exit: number
  points: number
  pnl_usd: number
  result: string
}

export interface RunResults {
  run_id: string
  strategy: string
  metrics: RunMetrics
  equity_curve: number[]
  drawdown_curve: number[]
  trades: Trade[]
  files: string[]
}
