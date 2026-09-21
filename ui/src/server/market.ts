import { createServerFn } from '@tanstack/react-start'
import type { AnalysisResponse } from '../types/market'

export const fetchMarketSignal = createServerFn({ method: 'GET' })
  .validator((params: { ticker: string; period: string; source: string }) => params)
  .handler(async ({ data: { ticker, period, source } }): Promise<AnalysisResponse> => {
    const rawCandidates = [
      process.env.INTERNAL_API_URL,
      process.env.API_URL,
      process.env.VITE_API_URL,
      // Render private network hostnames
      'http://algo-trading-api-prod:8000',
      'http://algo-trading-api-dev:8000',
      'http://algo-trading-api:8000',
      // Local development hostnames
      'http://127.0.0.1:8001',
      'http://127.0.0.1:8000',
      'http://localhost:8001',
      'http://localhost:8000',
    ].filter(Boolean) as string[]

    const urlsToTry = Array.from(
      new Set(
        rawCandidates.map((url) => {
          let trimmed = url.trim()
          if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
            trimmed = `http://${trimmed}`
          }
          return trimmed.replace(/\/+$/, '')
        })
      )
    )

    let lastError = ''
    for (const baseUrl of urlsToTry) {
      try {
        const queryParams = new URLSearchParams({ source })
        const targetUrl = `${baseUrl}/signal/${encodeURIComponent(ticker)}/${encodeURIComponent(period)}?${queryParams.toString()}`

        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 8000)

        const res = await fetch(targetUrl, {
          signal: controller.signal,
          headers: {
            Accept: 'application/json',
          },
        })
        clearTimeout(timeoutId)

        if (!res.ok) {
          const errBody = await res.json().catch(() => ({}))
          throw new Error(errBody.detail || `Backend responded with HTTP ${res.status}`)
        }

        const json = (await res.json()) as AnalysisResponse
        return json
      } catch (err: any) {
        lastError = err.message || 'Unknown network error'
      }
    }

    throw new Error(
      lastError ||
        `Failed to connect to Algo Trading API backend for ${ticker}. Candidate endpoints tried: ${urlsToTry.join(', ')}`
    )
  })
