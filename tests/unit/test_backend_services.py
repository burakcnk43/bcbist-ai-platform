import unittest
from types import SimpleNamespace

import pandas as pd

from backend.services.portfolio_service import PortfolioService
from backend.services.stock_registry import StockRegistryService
from backend.services.stock_service import StockService


class PortfolioServiceTests(unittest.TestCase):
    def test_upsert_and_summary(self) -> None:
        service = PortfolioService()

        payload = {
            "name": "Demo Portfolio",
            "positions": [
                {"symbol": "THYAO", "quantity": 10, "avg_cost": 100.0},
                {"symbol": "GARAN", "quantity": 5, "avg_cost": 80.0},
            ],
        }

        stored = service.upsert_portfolio(payload)
        self.assertEqual(stored["name"], "Demo Portfolio")
        self.assertEqual(len(stored["positions"]), 2)

        summary = service.get_portfolio_summary()
        self.assertEqual(summary["name"], "Demo Portfolio")
        self.assertEqual(summary["position_count"], 2)


class StockRegistryServiceTests(unittest.TestCase):
    def test_registry_contains_multiple_bist_symbols(self) -> None:
        service = StockRegistryService()

        registry = service.get_registry(limit=10)
        self.assertGreaterEqual(len(registry), 10)

        entry = service.get_symbol("THYAO")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["symbol"], "THYAO")
        self.assertEqual(entry["market"], "Borsa İstanbul")
        self.assertIn("listing_status", entry)


class StockServiceAnalysisTests(unittest.TestCase):
    def test_secondary_analysis_sections_are_built(self) -> None:
        service = StockService()
        history = pd.DataFrame(
            {
                "Close": [100, 101, 102, 103, 104, 105],
                "High": [101, 102, 103, 104, 105, 106],
                "Low": [99, 100, 101, 102, 103, 104],
                "Volume": [1000, 1100, 1200, 1300, 1400, 1500],
            }
        )
        summary = SimpleNamespace(
            rsi=60.0,
            macd=1.5,
            macd_signal=1.0,
            support=99.0,
            resistance=106.0,
            trend="Yukarı yönlü",
            explanations=["Teknik açıklama"],
        )

        payload = service._build_analysis_sections(
            history=history,
            summary=summary,
            financial_metrics={
                "revenue": 1000.0,
                "net_income": 100.0,
                "ebitda": 200.0,
                "equity": 500.0,
                "debt": 100.0,
                "operating_cash_flow": 120.0,
                "free_cash_flow": 80.0,
            },
            valuation_metrics={"pe": 10.0, "pb": 1.0, "ev_ebitda": 8.0, "graham": {"graham_recommendation": "İskontolu"}},
            info={"marketCap": 1000000.0, "sharesOutstanding": 1000.0},
            income=pd.DataFrame({"Net Income": [80.0, 100.0]}),
            balance=pd.DataFrame({"Total Assets": [1000.0, 1200.0], "Total Liabilities": [300.0, 400.0], "Retained Earnings": [200.0, 250.0]}),
            cashflow=pd.DataFrame({"Operating Cash Flow": [120.0, 130.0]}),
            latest_price=105.0,
        )

        self.assertGreaterEqual(payload["piotroski"]["score"], 0)
        self.assertGreaterEqual(payload["altman_z"]["score"], 0)
        self.assertIn("volatility_label", payload["risk_metrics"])
        self.assertIn("summary", payload["ai_summary"])
        self.assertGreaterEqual(payload["overall_score"]["score"], 0)


if __name__ == "__main__":
    unittest.main()
