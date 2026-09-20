import { createFileRoute, useNavigate } from '@tanstack/react-router'
import React, { useEffect, useState, useTransition } from 'react'
import {
  Search,
  TrendingUp,
  TrendingDown,
  Minus,
  Activity,
  BarChart2,
  LineChart,
  RefreshCw,
  Layers,
  Sparkles,
  Zap,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Database,
  ExternalLink,
  Target,
  Brain,
  Calculator,
  Award,
} from 'lucide-react'
import { FinancialChart } from '../components/FinancialChart'
import { ForecastCards } from '../components/ForecastCards'
import type { AnalysisResponse, ProviderSource } from '../types/market'

export interface DashboardSearch {
  ticker?: string
  period?: string
  source?: ProviderSource
  chartType?: 'candlestick' | 'line'
  showSMA?: boolean
  showForecast?: boolean
}

const VALID_SOURCES: ProviderSource[] = ['google', 'yahoo', 'tipranks', 'wallstreet', 'fmp', 'danelfin']

export const Route = createFileRoute('/')({
  validateSearch: (search: Record<string, unknown>): DashboardSearch => {
    return {
      ticker:
        typeof search.ticker === 'string' && search.ticker.trim()
          ? search.ticker.trim().toUpperCase()
          : 'AAPL',
      period:
        typeof search.period === 'string' && search.period.trim()
          ? (search.period.trim() as string)
          : '6mo',
      source: VALID_SOURCES.includes(search.source as ProviderSource)
        ? (search.source as ProviderSource)
        : 'google',
      chartType: search.chartType === 'line' ? 'line' : 'candlestick',
      showSMA: search.showSMA !== false && search.showSMA !== 'false',
      showForecast: search.showForecast !== false && search.showForecast !== 'false',
    }
  },
  component: Dashboard,
})

const POPULAR_TICKERS = [
  { symbol: 'AAPL', label: 'Apple' },
  { symbol: 'AMZN', label: 'Amazon' },
  { symbol: 'AMD', label: 'AMD' },
  { symbol: 'BYD', label: 'BYD' },
  { symbol: 'GOOG', label: 'Google' },
  { symbol: 'META', label: 'Meta' },
  { symbol: 'MSFT', label: 'Microsoft' },
  { symbol: 'NVDA', label: 'Nvidia' },
  { symbol: 'TSLA', label: 'Tesla' },
  { symbol: 'BTC-USD', label: 'Bitcoin' },
  { symbol: 'ETH-USD', label: 'Ethereum' },
  { symbol: 'SPY', label: 'S&P 500' },
]

const PERIOD_OPTIONS = [
  { value: '1mo', label: '1M' },
  { value: '3mo', label: '3M' },
  { value: '6mo', label: '6M' },
  { value: '1y', label: '1Y' },
  { value: '2y', label: '2Y' },
  { value: '5y', label: '5Y' },
]

function Dashboard() {
  const search = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })

  const currentTicker = search.ticker || 'AAPL'
  const currentPeriod = search.period || '6mo'
  const currentSource = search.source || 'yahoo'
  const chartType = search.chartType || 'candlestick'
  const showSMA = search.showSMA ?? true
  const showForecast = search.showForecast ?? true

  const [inputTicker, setInputTicker] = useState(currentTicker)
  const [data, setData] = useState<AnalysisResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [, startTransition] = useTransition()

  useEffect(() => {
    setInputTicker(currentTicker)
  }, [currentTicker])

  const updateUrlParams = (updates: Partial<DashboardSearch>) => {
    startTransition(() => {
      navigate({
        search: (prev: DashboardSearch) => ({
          ...prev,
          ...updates,
        }),
        replace: true,
      })
    })
  }

  const fetchData = async () => {
    setLoading(true)
    setError(null)

    const urlsToTry = [
      import.meta.env.VITE_API_URL,
      'http://localhost:8001',
      'http://localhost:8000',
    ].filter(Boolean) as string[]

    let lastErrMsg = ''
    for (const baseUrl of urlsToTry) {
      try {
        const queryParams = new URLSearchParams({
          source: currentSource,
        })
        const res = await fetch(
          `${baseUrl}/signal/${encodeURIComponent(currentTicker)}/${encodeURIComponent(currentPeriod)}?${queryParams.toString()}`
        )
        if (!res.ok) {
          const errBody = await res.json().catch(() => ({}))
          throw new Error(errBody.detail || `Server responded with ${res.status}`)
        }
        const json = (await res.json()) as AnalysisResponse
        setData(json)
        setLoading(false)
        return
      } catch (err: any) {
        lastErrMsg = err.message || 'Network request failed'
      }
    }

    setError(lastErrMsg || `Failed to fetch data for ${currentTicker}. Make sure the backend API is running.`)
    setLoading(false)
  }

  useEffect(() => {
    fetchData()
  }, [currentTicker, currentPeriod, currentSource])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputTicker.trim()) return
    updateUrlParams({ ticker: inputTicker.trim().toUpperCase() })
  }

  const isPricePositive = (data?.price_change_pct ?? 0) >= 0

  return (
    <div className="min-h-screen bg-[#060910] text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-[#060910]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/25">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold tracking-tight text-white">
                  AlgoTrading <span className="text-cyan-400">Terminal</span>
                </span>
                {/* Dynamic Environment Indicator */}
                {import.meta.env.VITE_APP_ENV === 'production' ? (
                  <span
                    title="Production Environment (Branch: main)"
                    className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-[10px] font-bold text-emerald-300 border border-emerald-500/30 shadow-sm shadow-emerald-500/20"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    PROD
                  </span>
                ) : (
                  <span
                    title="Development Environment (Branch: dev)"
                    className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/15 px-2.5 py-0.5 text-[10px] font-bold text-amber-300 border border-amber-500/30 shadow-sm shadow-amber-500/20"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse" />
                    DEV
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-400">Quantitative Signals & Market Forecasting</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Provider Combobox */}
            <div className="flex items-center gap-1.5 rounded-xl border border-slate-800 bg-slate-900/90 px-3 py-1.5 text-xs shadow-sm">
              <Database className="h-3.5 w-3.5 text-cyan-400" />
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider hidden sm:inline">
                Provider:
              </span>
              <select
                value={currentSource}
                onChange={(e) => updateUrlParams({ source: e.target.value as ProviderSource })}
                className="bg-transparent font-medium text-white focus:outline-none cursor-pointer text-xs pr-1"
                aria-label="Select Financial Data Provider"
              >
                <option value="google" className="bg-slate-900 text-white">
                  🔵 Google Finance
                </option>
                <option value="yahoo" className="bg-slate-900 text-white">
                  🟣 Yahoo Finance
                </option>
                <option value="tipranks" className="bg-slate-900 text-white">
                  🎯 TipRanks Analysts
                </option>
                <option value="wallstreet" className="bg-slate-900 text-white">
                  🏛️ Wall Street Consensus
                </option>
                <option value="fmp" className="bg-slate-900 text-white">
                  📊 FMP Valuation & DCF
                </option>
                <option value="danelfin" className="bg-slate-900 text-white">
                  🤖 Danelfin AI Quant
                </option>
              </select>
            </div>

            {/* Search Form */}
            <form onSubmit={handleSearchSubmit} className="relative hidden md:block w-64">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={inputTicker}
                onChange={(e) => setInputTicker(e.target.value)}
                placeholder="Search ticker (e.g. NVDA, BTC-USD)..."
                className="w-full rounded-xl border border-slate-800 bg-slate-900/90 py-2 pl-9 pr-4 text-xs text-white placeholder-slate-400 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all font-mono"
              />
            </form>
          </div>
        </div>

        {/* Ticker Presets & Period Switcher */}
        <div className="border-t border-slate-800/40 bg-slate-950/40 px-4 py-2 sm:px-6">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
            {/* Quick Chips */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
              <span className="text-[11px] font-semibold text-slate-400 mr-1 uppercase tracking-wider">
                Watchlist:
              </span>
              {POPULAR_TICKERS.map((item) => {
                const isActive = currentTicker === item.symbol
                return (
                  <button
                    key={item.symbol}
                    onClick={() => updateUrlParams({ ticker: item.symbol })}
                    className={`rounded-lg px-2.5 py-1 text-xs font-mono font-medium transition-all ${isActive
                      ? 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                      : 'bg-slate-900/80 text-slate-300 hover:bg-slate-800 hover:text-white border border-slate-800/60'
                      }`}
                  >
                    {item.symbol}
                  </button>
                )
              })}
            </div>

            {/* Period Switcher */}
            <div className="flex items-center gap-1 rounded-xl border border-slate-800/80 bg-slate-900/80 p-1">
              <Clock className="h-3.5 w-3.5 text-slate-400 ml-1.5 mr-0.5" />
              {PERIOD_OPTIONS.map((p) => {
                const isActive = currentPeriod === p.value
                return (
                  <button
                    key={p.value}
                    onClick={() => updateUrlParams({ period: p.value })}
                    className={`rounded-lg px-2.5 py-0.5 text-xs font-medium transition-all ${isActive
                      ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                      }`}
                  >
                    {p.label}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 space-y-6">
        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 space-y-4">
            <div className="relative h-12 w-12">
              <div className="absolute inset-0 rounded-full border-4 border-cyan-500/20 animate-ping" />
              <div className="h-12 w-12 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin" />
            </div>
            <div className="text-center">
              <h3 className="text-sm font-semibold text-slate-200">
                Fetching Analysis from {currentSource === 'google' ? 'Google Finance' : 'Yahoo Finance'} for {currentTicker}...
              </h3>
              <p className="text-xs text-slate-400">Computing moving averages and predicting future price path</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {!loading && error && (
          <div className="rounded-2xl border border-rose-800/50 bg-rose-950/20 p-6 text-center shadow-xl">
            <AlertTriangle className="mx-auto h-10 w-10 text-rose-400" />
            <h3 className="mt-3 text-base font-semibold text-rose-200">Analysis Unavailable</h3>
            <p className="mt-1 text-xs text-rose-300/80 max-w-md mx-auto">{error}</p>
            <div className="mt-4 flex items-center justify-center gap-3">
              <button
                onClick={fetchData}
                className="inline-flex items-center gap-1.5 rounded-xl bg-rose-600 px-4 py-2 text-xs font-medium text-white hover:bg-rose-500 shadow-lg shadow-rose-600/20 transition-all"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Retry
              </button>
              <button
                onClick={() => updateUrlParams({ ticker: 'AAPL', period: '6mo', source: 'yahoo' })}
                className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-700 transition-all"
              >
                Reset to AAPL (Yahoo)
              </button>
            </div>
          </div>
        )}

        {/* Content Loaded */}
        {!loading && data && (
          <>
            {/* Header Metrics Banner */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
              {/* Card 1: Asset & Price */}
              <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-xl shadow-xl">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="font-semibold uppercase tracking-wider">Asset Price</span>
                  <span className="font-mono text-[11px] text-slate-400">{data.latest_date}</span>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-bold font-mono text-white tracking-tight">
                    ${data.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                  <span className="text-xs font-bold text-slate-400">{data.ticker}</span>
                </div>
                <div className="mt-2 flex items-center gap-1.5 text-xs">
                  <span
                    className={`inline-flex items-center font-mono font-semibold ${isPricePositive ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                  >
                    {isPricePositive ? '+' : ''}
                    {data.price_change_pct.toFixed(2)}%
                  </span>
                  <span className="text-slate-400 font-mono">
                    ({isPricePositive ? '+' : ''}${data.price_change.toFixed(2)} in {data.period})
                  </span>
                </div>
                <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
                  <span>
                    Provider: <strong className="text-slate-200">{data.source_name || 'Yahoo Finance'}</strong>
                  </span>
                  {data.source_url && (
                    <a
                      href={data.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-cyan-400 hover:text-cyan-300 hover:underline"
                    >
                      Official Page <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>

              {/* Card 2: Algorithmic Signal */}
              <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-xl shadow-xl">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="font-semibold uppercase tracking-wider">Signal Strategy</span>
                  <Activity className="h-4 w-4 text-slate-400" />
                </div>
                <div className="mt-3 flex items-center gap-3">
                  <div
                    className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-base font-bold shadow-lg ${data.metrics.latest_signal === 1
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-emerald-500/20'
                      : data.metrics.latest_signal === -1
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 shadow-rose-500/20'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/40 shadow-amber-500/20'
                      }`}
                  >
                    {data.metrics.latest_signal === 1 ? (
                      <TrendingUp className="h-5 w-5 animate-bounce" />
                    ) : data.metrics.latest_signal === -1 ? (
                      <TrendingDown className="h-5 w-5 animate-bounce" />
                    ) : (
                      <Minus className="h-5 w-5" />
                    )}
                    <span>{data.metrics.latest_signal_label} SIGNAL</span>
                  </div>
                </div>
                <p className="mt-2 text-[11px] text-slate-400">
                  SMA 20 ({data.metrics.sma_20 ? `$${data.metrics.sma_20}` : '—'}) vs SMA 50 ({data.metrics.sma_50 ? `$${data.metrics.sma_50}` : '—'})
                </p>
              </div>

              {/* Card 3: Trend & Momentum */}
              <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-xl shadow-xl">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="font-semibold uppercase tracking-wider">Market Trend</span>
                  <CheckCircle2 className="h-4 w-4 text-cyan-400" />
                </div>
                <div className="mt-3">
                  <span className="text-xl font-bold tracking-tight text-cyan-300 font-mono">
                    {data.metrics.trend}
                  </span>
                </div>
                <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
                  <span>Cross Condition:</span>
                  <span className="font-mono text-slate-300">
                    {data.metrics.sma_20 && data.metrics.sma_50 && data.metrics.sma_20 > data.metrics.sma_50
                      ? 'Golden Alignment (Bullish)'
                      : 'Death Alignment (Bearish)'}
                  </span>
                </div>
              </div>

              {/* Card 4: Volatility & Risk */}
              <div className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-xl shadow-xl">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="font-semibold uppercase tracking-wider">Historical Volatility</span>
                  <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-300">Annualized</span>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-bold font-mono text-amber-400">
                    {data.metrics.volatility_annualized_pct.toFixed(1)}%
                  </span>
                  <span className="text-xs text-slate-400">
                    {data.metrics.volatility_annualized_pct > 40
                      ? 'High Risk'
                      : data.metrics.volatility_annualized_pct > 20
                        ? 'Moderate Risk'
                        : 'Low Risk'}
                  </span>
                </div>
                <p className="mt-2 text-[11px] text-slate-400">
                  Used as diffusion parameter $\sigma$ in the forward prediction engine
                </p>
              </div>
            </div>

            {/* Specialized Provider Intelligence Panel */}
            {data.provider_insights && (
              data.provider_insights.analyst_consensus ||
              data.provider_insights.valuation_dcf ||
              data.provider_insights.ai_prediction
            ) && (
                <div className="rounded-2xl border border-cyan-500/20 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-cyan-950/20 p-4 shadow-xl backdrop-blur-xl">
                  {/* TipRanks or Wall Street Consensus */}
                  {data.provider_insights.analyst_consensus && (
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className="rounded-xl bg-cyan-500/10 p-2.5 text-cyan-400 border border-cyan-500/20">
                          <Target className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                              {data.source === 'tipranks' ? '🎯 TipRanks Top Analysts' : '🏛️ Wall Street Institutional Consensus'}
                            </span>
                            {data.provider_insights.analyst_consensus.consensus_rating && (
                              <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-bold text-emerald-400 border border-emerald-500/20">
                                {data.provider_insights.analyst_consensus.consensus_rating}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-300 mt-0.5">
                            12-Month Price Target: <strong className="font-mono text-white text-sm">${data.provider_insights.analyst_consensus.target_mean?.toFixed(2) ?? 'N/A'}</strong>
                            {data.provider_insights.analyst_consensus.target_mean && data.current_price > 0 && (
                              <span className={`ml-2 font-mono font-semibold ${data.provider_insights.analyst_consensus.target_mean >= data.current_price ? 'text-emerald-400' : 'text-rose-400'}`}>
                                ({((data.provider_insights.analyst_consensus.target_mean - data.current_price) / data.current_price * 100).toFixed(1)}% implied upside)
                              </span>
                            )}
                          </p>
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-3 text-xs">
                        {data.provider_insights.analyst_consensus.target_low && data.provider_insights.analyst_consensus.target_high && (
                          <div className="rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-1.5 font-mono text-slate-300">
                            <span className="text-[10px] text-slate-400 block uppercase">Target Corridor</span>
                            ${data.provider_insights.analyst_consensus.target_low?.toFixed(2)} - ${data.provider_insights.analyst_consensus.target_high?.toFixed(2)}
                          </div>
                        )}
                        {(data.provider_insights.analyst_consensus.buy_count !== null && data.provider_insights.analyst_consensus.buy_count !== undefined && data.provider_insights.analyst_consensus.buy_count > 0) && (
                          <div className="flex items-center gap-1.5 rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-1.5">
                            <span className="text-emerald-400 font-bold">{data.provider_insights.analyst_consensus.buy_count} Buy</span>
                            <span className="text-slate-600">/</span>
                            <span className="text-amber-400 font-bold">{data.provider_insights.analyst_consensus.hold_count} Hold</span>
                            <span className="text-slate-600">/</span>
                            <span className="text-rose-400 font-bold">{data.provider_insights.analyst_consensus.sell_count} Sell</span>
                          </div>
                        )}
                        {data.provider_insights.analyst_consensus.analyst_opinions_count && (
                          <div className="rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-1.5 text-slate-400">
                            Based on <strong className="text-white">{data.provider_insights.analyst_consensus.analyst_opinions_count}</strong> Analyst Opinions
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* FMP DCF Valuation */}
                  {data.provider_insights.valuation_dcf && (
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className="rounded-xl bg-violet-500/10 p-2.5 text-violet-400 border border-violet-500/20">
                          <Calculator className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold uppercase tracking-wider text-violet-400">
                              📊 Financial Modeling Prep (FMP) DCF Valuation
                            </span>
                            {data.provider_insights.valuation_dcf.status && (
                              <span className="rounded-full bg-violet-500/10 px-2.5 py-0.5 text-xs font-bold text-violet-300 border border-violet-500/20">
                                {data.provider_insights.valuation_dcf.status}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-300 mt-0.5">
                            Intrinsic Fair Value: <strong className="font-mono text-white text-sm">${data.provider_insights.valuation_dcf.intrinsic_value?.toFixed(2) ?? 'N/A'}</strong>
                            {data.provider_insights.valuation_dcf.upside_pct !== null && data.provider_insights.valuation_dcf.upside_pct !== undefined && (
                              <span className={`ml-2 font-mono font-semibold ${data.provider_insights.valuation_dcf.upside_pct >= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                                ({data.provider_insights.valuation_dcf.upside_pct > 0 ? '+' : ''}{data.provider_insights.valuation_dcf.upside_pct.toFixed(1)}% valuation gap)
                              </span>
                            )}
                          </p>
                        </div>
                      </div>

                      <div className="rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-1.5 text-[11px] text-slate-400 max-w-sm">
                        Calculated via 5-Year Free Cash Flow Projections + Terminal Enterprise Value Discounted Cash Flow Model
                      </div>
                    </div>
                  )}

                  {/* Danelfin AI Quant Score */}
                  {data.provider_insights.ai_prediction && (
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className="rounded-xl bg-emerald-500/10 p-2.5 text-emerald-400 border border-emerald-500/20">
                          <Brain className="h-5 w-5 animate-pulse" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                              🤖 Danelfin Explainable AI Stock Score
                            </span>
                            {data.provider_insights.ai_prediction.conviction && (
                              <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-xs font-bold text-emerald-300 border border-emerald-500/30">
                                {data.provider_insights.ai_prediction.conviction}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-300 mt-0.5">
                            Multi-Factor AI Score: <strong className="font-mono text-emerald-400 text-base">{data.provider_insights.ai_prediction.score}/10</strong>
                            {data.provider_insights.ai_prediction.outperformance_probability_pct && (
                              <span className="ml-2 text-slate-300">
                                • <strong className="font-mono text-white">{data.provider_insights.ai_prediction.outperformance_probability_pct}%</strong> probability of outperforming S&P 500
                              </span>
                            )}
                          </p>
                        </div>
                      </div>

                      <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/20 px-3.5 py-1.5 text-xs text-emerald-300 font-medium">
                        ✓ Technical Momentum, Fundamental Health & Sentiment Alpha
                      </div>
                    </div>
                  )}
                </div>
              )}

            {/* Chart Control Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/50 p-3 shadow-lg backdrop-blur-md">
              <div className="flex flex-wrap items-center gap-2">
                {/* Candlestick vs Line Toggle */}
                <div className="flex items-center rounded-xl border border-slate-800 bg-slate-950 p-1">
                  <button
                    onClick={() => updateUrlParams({ chartType: 'candlestick' })}
                    className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-medium transition-all ${chartType === 'candlestick'
                      ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                      }`}
                  >
                    <BarChart2 className="h-3.5 w-3.5" />
                    Candlesticks
                  </button>
                  <button
                    onClick={() => updateUrlParams({ chartType: 'line' })}
                    className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-medium transition-all ${chartType === 'line'
                      ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                      }`}
                  >
                    <LineChart className="h-3.5 w-3.5" />
                    Line
                  </button>
                </div>

                {/* SMA Overlay Toggle */}
                <button
                  onClick={() => updateUrlParams({ showSMA: !showSMA })}
                  className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-medium transition-all ${showSMA
                    ? 'border-amber-500/40 bg-amber-500/10 text-amber-300'
                    : 'border-slate-800 bg-slate-950 text-slate-400 hover:text-white'
                    }`}
                >
                  <Layers className="h-3.5 w-3.5" />
                  SMA 20 & 50
                </button>

                {/* Forecast Overlay Toggle */}
                <button
                  onClick={() => updateUrlParams({ showForecast: !showForecast })}
                  className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-medium transition-all ${showForecast
                    ? 'border-sky-500/40 bg-sky-500/10 text-sky-300'
                    : 'border-slate-800 bg-slate-950 text-slate-400 hover:text-white'
                    }`}
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  AI Future Horizon
                </button>
              </div>

              {/* Refresh Button */}
              <div className="flex items-center gap-2">
                <button
                  onClick={fetchData}
                  className="flex items-center gap-1.5 rounded-xl border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs font-medium text-slate-300 hover:border-slate-700 hover:text-white transition-all"
                  title="Reload current ticker data"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  Refresh
                </button>
              </div>
            </div>

            {/* Interactive Financial Chart */}
            <FinancialChart
              historical={data.historical}
              forecast={data.forecast}
              ticker={data.ticker}
              chartType={chartType}
              showSMA={showSMA}
              showForecast={showForecast}
            />

            {/* Future Horizon Predictions Section */}
            <ForecastCards
              forecast7d={data.metrics.forecast_7d}
              forecast14d={data.metrics.forecast_14d}
              forecast30d={data.metrics.forecast_30d}
              currentPrice={data.current_price}
              volatilityPct={data.metrics.volatility_annualized_pct}
            />

            {/* Historical Crossovers Timeline */}
            <div className="rounded-2xl border border-slate-800/80 bg-slate-900/50 p-5 shadow-xl backdrop-blur-md">
              <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-cyan-400" />
                  <h3 className="text-sm font-semibold text-white">Historical Crossover Signals</h3>
                </div>
                <span className="text-xs text-slate-400 font-mono">
                  SMA 20 / SMA 50 Strategy
                </span>
              </div>

              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-2 font-medium">Date</th>
                      <th className="pb-2 font-medium">Signal</th>
                      <th className="pb-2 font-medium">Price at Event</th>
                      <th className="pb-2 font-medium">SMA 20</th>
                      <th className="pb-2 font-medium">SMA 50</th>
                      <th className="pb-2 font-medium text-right">Performance to Current</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {data.historical
                      .filter((h) => h.crossover !== null)
                      .slice(-5)
                      .reverse()
                      .map((event, idx) => {
                        const priceAtEvent = event.close
                        const perfPct = ((data.current_price - priceAtEvent) / priceAtEvent) * 100
                        const isBuy = event.crossover === 'BUY'

                        return (
                          <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                            <td className="py-2.5 text-slate-300">{event.time}</td>
                            <td className="py-2.5">
                              <span
                                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-bold ${isBuy
                                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                  }`}
                              >
                                {isBuy ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                                {event.crossover}
                              </span>
                            </td>
                            <td className="py-2.5 text-white font-semibold">${event.close.toFixed(2)}</td>
                            <td className="py-2.5 text-amber-400">${event.sma_20?.toFixed(2) || '—'}</td>
                            <td className="py-2.5 text-purple-400">${event.sma_50?.toFixed(2) || '—'}</td>
                            <td className="py-2.5 text-right font-bold">
                              <span className={perfPct >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                                {perfPct >= 0 ? '+' : ''}
                                {perfPct.toFixed(2)}%
                              </span>
                            </td>
                          </tr>
                        )
                      })}
                    {data.historical.filter((h) => h.crossover !== null).length === 0 && (
                      <tr>
                        <td colSpan={6} className="py-4 text-center text-slate-400">
                          No SMA crossover events occurred during the selected period.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#060910] px-4 py-4 text-center text-xs text-slate-400">
        <p>
          AlgoTrading Platform &bull; Data from {data?.source_name || 'Yahoo & Google Finance'} &bull;{' '}
          <span className="text-slate-400">All analytical filters & providers stored in URL for sharing</span>
        </p>
      </footer>
    </div>
  )
}
