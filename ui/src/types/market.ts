export interface HistoricalBar {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  sma_20: number | null
  sma_50: number | null
  signal: number
  crossover: 'BUY' | 'SELL' | null
}

export interface ForecastBar {
  time: string
  predicted_close: number
  upper_bound: number
  lower_bound: number
}

export interface HorizonForecast {
  date: string
  target_price: number
  upper_bound: number
  lower_bound: number
  expected_change_pct: number
  direction: 'Bullish' | 'Bearish' | 'Neutral'
}

export interface AnalysisMetrics {
  latest_signal: number
  latest_signal_label: 'BUY' | 'SELL' | 'HOLD'
  trend: string
  sma_20: number | null
  sma_50: number | null
  volatility_annualized_pct: number
  forecast_7d: HorizonForecast
  forecast_14d: HorizonForecast
  forecast_30d: HorizonForecast
}

export interface AnalysisResponse {
  ticker: string
  period: string
  source?: 'yahoo' | 'google'
  source_name?: string
  source_url?: string
  current_price: number
  price_change: number
  price_change_pct: number
  latest_date: string
  historical: HistoricalBar[]
  forecast: ForecastBar[]
  metrics: AnalysisMetrics
  disclaimer: string
}
