"""
Unit and integration tests for technical analysis, forecasting, providers, and API routes.
"""
import unittest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from api.main import app
from api.services.technical_analysis import (
    compute_technical_indicators,
    determine_market_trend,
    get_latest_signal_label,
)
from api.services.forecasting import (
    calculate_drift_and_volatility,
    generate_gbm_forecast,
    calculate_horizon_projection,
)
from api.services.market_service import market_service


class TestTechnicalAnalysis(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range(start="2026-01-01", periods=60, freq="B")
        prices = [100.0 + i * 0.5 for i in range(60)]
        self.df = pd.DataFrame(
            {
                "Open": prices,
                "High": [p + 1.0 for p in prices],
                "Low": [p - 1.0 for p in prices],
                "Close": prices,
                "Volume": [10000] * 60,
            },
            index=dates,
        )

    def test_compute_technical_indicators(self):
        res = compute_technical_indicators(self.df)
        self.assertIn("SMA_20", res.columns)
        self.assertIn("SMA_50", res.columns)
        self.assertIn("Signal", res.columns)
        self.assertIn("Crossover", res.columns)
        self.assertEqual(res["Signal"].iloc[-1], 1)

    def test_determine_market_trend(self):
        trend = determine_market_trend(sma_20=150.0, sma_50=140.0, last_price=155.0)
        self.assertEqual(trend, "STRONG BULLISH")

        trend_bear = determine_market_trend(sma_20=130.0, sma_50=140.0, last_price=125.0)
        self.assertEqual(trend_bear, "STRONG BEARISH")

    def test_signal_labels(self):
        self.assertEqual(get_latest_signal_label(1), "BUY")
        self.assertEqual(get_latest_signal_label(-1), "SELL")
        self.assertEqual(get_latest_signal_label(0), "HOLD")


class TestForecasting(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        close_vals = 100.0 * np.exp(np.cumsum(np.random.normal(0.001, 0.015, 60)))
        self.close_series = pd.Series(close_vals)
        self.last_date = pd.Timestamp("2026-06-01")

    def test_drift_and_volatility(self):
        drift, daily_vol, ann_vol = calculate_drift_and_volatility(self.close_series)
        self.assertGreater(daily_vol, 0.0)
        self.assertGreater(ann_vol, 0.0)

    def test_generate_gbm_forecast(self):
        drift, daily_vol, _ = calculate_drift_and_volatility(self.close_series)
        forecast = generate_gbm_forecast(150.0, self.last_date, drift, daily_vol, days=30)
        self.assertEqual(len(forecast), 31)
        for point in forecast:
            self.assertGreaterEqual(point["upper_bound"], point["predicted_close"])
            self.assertLessEqual(point["lower_bound"], point["predicted_close"])

    def test_horizon_projection(self):
        target = {
            "time": "2026-06-10",
            "predicted_close": 160.0,
            "upper_bound": 170.0,
            "lower_bound": 150.0,
        }
        res = calculate_horizon_projection(target, last_price=150.0)
        self.assertEqual(res["direction"], "Bullish")
        self.assertGreater(res["expected_change_pct"], 0.0)


class TestProviders(unittest.TestCase):
    def test_tipranks_provider(self):
        p = market_service.get_provider("tipranks")
        quote = p.get_realtime_quote("AAPL")
        self.assertIsNotNone(quote)
        self.assertEqual(quote.source, "tipranks")
        self.assertIn("tipranks.com", quote.url)

    def test_wallstreet_provider(self):
        p = market_service.get_provider("wallstreet")
        quote = p.get_realtime_quote("AAPL")
        self.assertIsNotNone(quote)
        self.assertEqual(quote.source, "wallstreet")
        self.assertIsNotNone(quote.consensus_rating)

    def test_fmp_provider(self):
        p = market_service.get_provider("fmp")
        quote = p.get_realtime_quote("AAPL")
        self.assertIsNotNone(quote)
        self.assertEqual(quote.source, "fmp")
        self.assertIsNotNone(quote.dcf_intrinsic_value)

    def test_danelfin_provider(self):
        p = market_service.get_provider("danelfin")
        quote = p.get_realtime_quote("AAPL")
        self.assertIsNotNone(quote)
        self.assertEqual(quote.source, "danelfin")
        self.assertIsNotNone(quote.ai_score)
        self.assertTrue(1 <= quote.ai_score <= 10)


class TestApiRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")

    def test_all_provider_sources(self):
        sources = ["google", "yahoo", "tipranks", "wallstreet", "fmp", "danelfin"]
        for s in sources:
            response = self.client.get(f"/signal/AAPL/1mo?source={s}")
            self.assertEqual(response.status_code, 200, f"Source {s} failed with {response.status_code}")
            data = response.json()
            self.assertEqual(data["source"], s)
            self.assertIn("provider_insights", data)

    def test_forecast_endpoint(self):
        response = self.client.get("/forecast/AAPL?period=1mo&source=tipranks")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ticker"], "AAPL")
        self.assertEqual(data["source"], "tipranks")
        self.assertIn("forecast", data)
        self.assertIn("provider_insights", data)


if __name__ == "__main__":
    unittest.main()
