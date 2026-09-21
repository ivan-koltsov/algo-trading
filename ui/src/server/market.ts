import { createServerFn } from '@tanstack/react-start'
import type { AnalysisResponse } from '../types/market'

export const fetchMarketSignal = createServerFn({ method: 'GET' })
  .validator((params: { ticker: string; period: string; source: string }) => params)
  .handler(async ({ data: { ticker, period, source } }): Promise<AnalysisResponse> => {
    const isProd =
      process.env.APP_ENV === 'production' ||
      process.env.VITE_APP_ENV === 'production' ||
      process.env.NODE_ENV === 'production'

    const rawCandidates: (string | undefined)[] = [
      process.env.INTERNAL_API_URL,
      process.env.API_URL,
      process.env.VITE_API_URL,
      // Render private network hostnames
      'http://algo-trading-api-prod:8000',
      'http://algo-trading-api-dev:8000',
      'http://algo-trading-api:8000',
      'http://api:8000', // Docker Compose bridge network
      // Cloud Public Endpoints
      'https://algo-trading-api-prod.onrender.com',
      'https://algo-trading-api-dev.onrender.com',
      'https://algo-trading-api.onrender.com',
      // Local Host Dev / Prod fallbacks (prioritize based on active environment)
      isProd ? 'http://127.0.0.1:8000' : 'http://127.0.0.1:8001',
      isProd ? 'http://localhost:8000' : 'http://localhost:8001',
      isProd ? 'http://127.0.0.1:8001' : 'http://127.0.0.1:8000',
      isProd ? 'http://localhost:8001' : 'http://localhost:8000',
    ]

    const urlsToTry: string[] = []
    const seen = new Set<string>()

    for (const raw of rawCandidates) {
      if (!raw) continue
      let trimmed = raw.trim()
      if (!trimmed) continue

      // Ensure protocol scheme is present
      if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
        trimmed = `http://${trimmed}`
      }

      // If internal hostname without port, default to :8000
      try {
        const parsed = new URL(trimmed)
        if (!parsed.port && !parsed.hostname.includes('.')) {
          parsed.port = '8000'
          trimmed = parsed.toString()
        }
      } catch {
        // preserve trimmed as is
      }

      const clean = trimmed.replace(/\/+$/, '')
      if (!seen.has(clean)) {
        seen.add(clean)
        urlsToTry.push(clean)
      }
    }

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
