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

export interface AnalystConsensusInsight {
  target_mean?: number | null
  target_high?: number | null
  target_low?: number | null
  consensus_rating?: string | null
  buy_count?: number | null
  hold_count?: number | null
  sell_count?: number | null
  analyst_opinions_count?: number | null
}

export interface ValuationDCFInsight {
  intrinsic_value?: number | null
  upside_pct?: number | null
  status?: string | null
}

export interface AIPredictionInsight {
  score?: number | null
  outperformance_probability_pct?: number | null
  conviction?: string | null
}

export interface ProviderInsights {
  analyst_consensus?: AnalystConsensusInsight | null
  valuation_dcf?: ValuationDCFInsight | null
  ai_prediction?: AIPredictionInsight | null
}

export type ProviderSource = 'google' | 'yahoo' | 'tipranks' | 'wallstreet' | 'fmp' | 'danelfin'

export interface AnalysisResponse {
  ticker: string
  period: string
  source?: ProviderSource
  source_name?: string
  source_url?: string
  current_price: number
  price_change: number
  price_change_pct: number
  latest_date: string
  historical: HistoricalBar[]
  forecast: ForecastBar[]
  metrics: AnalysisMetrics
  provider_insights?: ProviderInsights
  disclaimer: string
}
