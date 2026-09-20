import React from 'react'
import { TrendingUp, TrendingDown, Minus, Calendar, Sparkles, AlertCircle } from 'lucide-react'
import type { HorizonForecast } from '../types/market'

interface ForecastCardsProps {
  forecast7d: HorizonForecast
  forecast14d: HorizonForecast
  forecast30d: HorizonForecast
  currentPrice: number
  volatilityPct: number
}

interface HorizonCardProps {
  title: string
  subtitle: string
  data: HorizonForecast
  currentPrice: number
}

const HorizonCard: React.FC<HorizonCardProps> = ({ title, subtitle, data, currentPrice }) => {
  const isBullish = data.expected_change_pct > 0
  const isNeutral = Math.abs(data.expected_change_pct) <= 0.5
  const deltaPrice = data.target_price - currentPrice

  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-800/80 bg-gradient-to-b from-slate-900/90 to-slate-950/80 p-5 shadow-xl backdrop-blur-md transition-all hover:border-slate-700 hover:shadow-cyan-950/20">
      {/* Top Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              {title}
            </span>
            <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300">
              {subtitle}
            </span>
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-xs text-slate-400">
            <Calendar className="h-3 w-3 text-slate-400" />
            <span>Target: {data.date}</span>
          </div>
        </div>

        {/* Direction Badge */}
        <span
          className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${
            isNeutral
              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              : isBullish
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
          }`}
        >
          {isNeutral ? (
            <Minus className="h-3 w-3" />
          ) : isBullish ? (
            <TrendingUp className="h-3 w-3" />
          ) : (
            <TrendingDown className="h-3 w-3" />
          )}
          {data.direction}
        </span>
      </div>

      {/* Target Price and Delta */}
      <div className="mt-4 flex items-baseline justify-between">
        <div>
          <div className="text-2xl font-bold tracking-tight text-white font-mono">
            ${data.target_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-xs text-slate-400">
            Expected Change:
          </div>
        </div>

        <div className="text-right">
          <div
            className={`text-lg font-bold font-mono ${
              isNeutral ? 'text-amber-400' : isBullish ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {data.expected_change_pct >= 0 ? '+' : ''}
            {data.expected_change_pct.toFixed(2)}%
          </div>
          <div className="text-xs font-mono text-slate-400">
            {deltaPrice >= 0 ? '+' : ''}${deltaPrice.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Confidence Corridor (90% Interval) */}
      <div className="mt-4 rounded-xl border border-slate-800/60 bg-slate-950/60 p-3">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span>90% Confidence Interval:</span>
          <span className="font-mono text-slate-300">
            ${data.lower_bound.toFixed(2)} — ${data.upper_bound.toFixed(2)}
          </span>
        </div>

        {/* Visual Corridor Bar */}
        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
          <div
            className={`h-full rounded-full transition-all ${
              isBullish ? 'bg-gradient-to-r from-emerald-500 to-cyan-400' : 'bg-gradient-to-r from-rose-500 to-amber-400'
            }`}
            style={{
              width: `${Math.min(100, Math.max(10, ((data.target_price - data.lower_bound) / (data.upper_bound - data.lower_bound || 1)) * 100))}%`,
            }}
          />
        </div>
      </div>
    </div>
  )
}

export const ForecastCards: React.FC<ForecastCardsProps> = ({
  forecast7d,
  forecast14d,
  forecast30d,
  currentPrice,
  volatilityPct,
}) => {
  return (
    <div className="w-full space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">
              Quantitative YFinance Predictions
            </h3>
            <p className="text-xs text-slate-400">
              Forward projections based on momentum drift and annualized volatility ({volatilityPct.toFixed(1)}%)
            </p>
          </div>
        </div>
      </div>

      {/* 3 Horizon Grid Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <HorizonCard
          title="7 Days Ahead"
          subtitle="Next Week"
          data={forecast7d}
          currentPrice={currentPrice}
        />
        <HorizonCard
          title="14 Days Ahead"
          subtitle="2 Weeks"
          data={forecast14d}
          currentPrice={currentPrice}
        />
        <HorizonCard
          title="30 Days Ahead"
          subtitle="1 Month"
          data={forecast30d}
          currentPrice={currentPrice}
        />
      </div>

      {/* Simulation Disclaimer Note */}
      <div className="flex items-center gap-2 text-[11px] text-slate-400">
        <AlertCircle className="h-3.5 w-3.5 text-slate-400 flex-shrink-0" />
        <span>
          Forecasts use drift-adjusted Geometric Brownian Motion and linear trend momentum. Financial markets carry inherent risk.
        </span>
      </div>
    </div>
  )
}
