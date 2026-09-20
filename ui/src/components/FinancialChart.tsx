import React, { useEffect, useRef, useState } from 'react'
import {
  createChart,
  CandlestickSeries,
  LineSeries,
  LineStyle,
  ColorType,
  createSeriesMarkers,
  type IChartApi,
  type ISeriesApi,
} from 'lightweight-charts'
import type { HistoricalBar, ForecastBar } from '../types/market'

interface FinancialChartProps {
  historical: HistoricalBar[]
  forecast: ForecastBar[]
  ticker: string
  chartType: 'candlestick' | 'line'
  showSMA: boolean
  showForecast: boolean
}

interface HoverLegendData {
  time: string
  open?: number
  high?: number
  low?: number
  close?: number
  sma_20?: number | null
  sma_50?: number | null
}

export const FinancialChart: React.FC<FinancialChartProps> = ({
  historical,
  forecast,
  ticker,
  chartType,
  showSMA,
  showForecast,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const [legendData, setLegendData] = useState<HoverLegendData | null>(null)

  useEffect(() => {
    if (!containerRef.current || historical.length === 0) return

    // Clean up previous chart instance if exists
    if (chartRef.current) {
      chartRef.current.remove()
      chartRef.current = null
    }

    const container = containerRef.current
    const chart = createChart(container, {
      width: container.clientWidth,
      height: 520,
      layout: {
        background: { type: ColorType.Solid, color: '#090d16' },
        textColor: '#94a3b8',
        fontSize: 12,
        fontFamily: 'system-ui, -apple-system, sans-serif',
      },
      grid: {
        vertLines: { color: 'rgba(30, 41, 59, 0.5)' },
        horzLines: { color: 'rgba(30, 41, 59, 0.5)' },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          color: '#38bdf8',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#0f172a',
        },
        horzLine: {
          color: '#38bdf8',
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: '#0f172a',
        },
      },
      timeScale: {
        borderColor: '#1e293b',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: '#1e293b',
        scaleMargins: {
          top: 0.1,
          bottom: 0.15,
        },
      },
    })

    chartRef.current = chart

    // 1. Primary Price Series (Candlesticks or Line)
    let mainSeries: ISeriesApi<'Candlestick'> | ISeriesApi<'Line'>

    if (chartType === 'candlestick') {
      const candleSeries = chart.addSeries(CandlestickSeries, {
        upColor: '#10b981',
        downColor: '#ef4444',
        borderVisible: false,
        wickUpColor: '#10b981',
        wickDownColor: '#ef4444',
      })

      const candleData = historical.map((d) => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }))
      candleSeries.setData(candleData)
      mainSeries = candleSeries
    } else {
      const lineSeries = chart.addSeries(LineSeries, {
        color: '#06b6d4',
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 4,
      })

      const lineData = historical.map((d) => ({
        time: d.time,
        value: d.close,
      }))
      lineSeries.setData(lineData)
      mainSeries = lineSeries
    }

    // 2. Buy / Sell Crossover Markers
    const markers: Array<{
      time: string
      position: 'aboveBar' | 'belowBar'
      color: string
      shape: 'arrowUp' | 'arrowDown'
      text: string
    }> = []

    historical.forEach((d) => {
      if (d.crossover === 'BUY') {
        markers.push({
          time: d.time,
          position: 'belowBar',
          color: '#10b981',
          shape: 'arrowUp',
          text: 'BUY',
        })
      } else if (d.crossover === 'SELL') {
        markers.push({
          time: d.time,
          position: 'aboveBar',
          color: '#ef4444',
          shape: 'arrowDown',
          text: 'SELL',
        })
      }
    })

    if (markers.length > 0) {
      try {
        createSeriesMarkers(mainSeries, markers)
      } catch (e) {
        console.warn('Could not set series markers:', e)
      }
    }

    // 3. Technical Indicators (SMA 20 & SMA 50)
    if (showSMA) {
      const sma20Data = historical
        .filter((d) => d.sma_20 !== null)
        .map((d) => ({ time: d.time, value: d.sma_20 as number }))

      if (sma20Data.length > 0) {
        const sma20Series = chart.addSeries(LineSeries, {
          color: '#f59e0b',
          lineWidth: 2,
          title: 'SMA 20',
          crosshairMarkerVisible: false,
        })
        sma20Series.setData(sma20Data)
      }

      const sma50Data = historical
        .filter((d) => d.sma_50 !== null)
        .map((d) => ({ time: d.time, value: d.sma_50 as number }))

      if (sma50Data.length > 0) {
        const sma50Series = chart.addSeries(LineSeries, {
          color: '#8b5cf6',
          lineWidth: 2,
          title: 'SMA 50',
          crosshairMarkerVisible: false,
        })
        sma50Series.setData(sma50Data)
      }
    }

    // 4. Predictive Forecast Horizon Series (Next Days & Weeks)
    if (showForecast && forecast.length > 0) {
      // Median / Mean projected path (Dashed Sky Blue)
      const forecastSeries = chart.addSeries(LineSeries, {
        color: '#38bdf8',
        lineWidth: 2,
        lineStyle: LineStyle.Dashed,
        title: 'Projected Path',
      })
      forecastSeries.setData(
        forecast.map((f) => ({
          time: f.time,
          value: f.predicted_close,
        }))
      )

      // Upper 90% Confidence Interval (Dotted)
      const upperSeries = chart.addSeries(LineSeries, {
        color: 'rgba(56, 189, 248, 0.45)',
        lineWidth: 1,
        lineStyle: LineStyle.Dotted,
        title: 'Upper 90%',
      })
      upperSeries.setData(
        forecast.map((f) => ({
          time: f.time,
          value: f.upper_bound,
        }))
      )

      // Lower 90% Confidence Interval (Dotted)
      const lowerSeries = chart.addSeries(LineSeries, {
        color: 'rgba(56, 189, 248, 0.45)',
        lineWidth: 1,
        lineStyle: LineStyle.Dotted,
        title: 'Lower 90%',
      })
      lowerSeries.setData(
        forecast.map((f) => ({
          time: f.time,
          value: f.lower_bound,
        }))
      )
    }

    // Initial legend: show latest historical bar
    const lastBar = historical[historical.length - 1]
    setLegendData({
      time: lastBar.time,
      open: lastBar.open,
      high: lastBar.high,
      low: lastBar.low,
      close: lastBar.close,
      sma_20: lastBar.sma_20,
      sma_50: lastBar.sma_50,
    })

    // Crosshair movement subscription
    chart.subscribeCrosshairMove((param) => {
      if (!param.time || !param.seriesData) {
        setLegendData({
          time: lastBar.time,
          open: lastBar.open,
          high: lastBar.high,
          low: lastBar.low,
          close: lastBar.close,
          sma_20: lastBar.sma_20,
          sma_50: lastBar.sma_50,
        })
        return
      }

      const timeStr = typeof param.time === 'string' ? param.time : ''
      const histMatch = historical.find((h) => h.time === timeStr)
      if (histMatch) {
        setLegendData({
          time: histMatch.time,
          open: histMatch.open,
          high: histMatch.high,
          low: histMatch.low,
          close: histMatch.close,
          sma_20: histMatch.sma_20,
          sma_50: histMatch.sma_50,
        })
      }
    })

    chart.timeScale().fitContent()

    // Responsive resize handler
    const resizeObserver = new ResizeObserver((entries) => {
      if (entries.length > 0 && chartRef.current) {
        const { width } = entries[0].contentRect
        chartRef.current.applyOptions({ width })
      }
    })

    resizeObserver.observe(container)

    return () => {
      resizeObserver.disconnect()
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
      }
    }
  }, [historical, forecast, chartType, showSMA, showForecast, ticker])

  return (
    <div className="relative w-full rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 shadow-2xl backdrop-blur-xl">
      {/* Dynamic Hover Legend */}
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/60 pb-3 text-xs">
        <div className="flex flex-wrap items-center gap-4">
          <span className="font-semibold text-slate-200">
            {ticker} <span className="text-slate-400 font-normal">({legendData?.time || '—'})</span>
          </span>
          {legendData?.open !== undefined && (
            <span className="text-slate-400">
              O: <strong className="font-mono text-slate-200">${legendData.open.toFixed(2)}</strong>
            </span>
          )}
          {legendData?.high !== undefined && (
            <span className="text-slate-400">
              H: <strong className="font-mono text-emerald-400">${legendData.high.toFixed(2)}</strong>
            </span>
          )}
          {legendData?.low !== undefined && (
            <span className="text-slate-400">
              L: <strong className="font-mono text-rose-400">${legendData.low.toFixed(2)}</strong>
            </span>
          )}
          {legendData?.close !== undefined && (
            <span className="text-slate-400">
              C: <strong className="font-mono text-cyan-300">${legendData.close.toFixed(2)}</strong>
            </span>
          )}
        </div>

        {/* Legend Indicators */}
        <div className="flex flex-wrap items-center gap-3">
          {showSMA && (
            <>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-amber-500"></span>
                <span className="text-slate-400">
                  SMA 20: <span className="font-mono text-amber-400">{legendData?.sma_20 ? `$${legendData.sma_20.toFixed(2)}` : '—'}</span>
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-purple-500"></span>
                <span className="text-slate-400">
                  SMA 50: <span className="font-mono text-purple-400">{legendData?.sma_50 ? `$${legendData.sma_50.toFixed(2)}` : '—'}</span>
                </span>
              </div>
            </>
          )}
          {showForecast && (
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-sky-400"></span>
              <span className="text-sky-400">AI Forecast Horizon</span>
            </div>
          )}
        </div>
      </div>

      {/* Chart Canvas Container */}
      <div ref={containerRef} className="w-full min-h-[520px] rounded-xl overflow-hidden" />
    </div>
  )
}
