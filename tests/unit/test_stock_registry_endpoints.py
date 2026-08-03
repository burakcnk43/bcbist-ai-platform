import unittest

from backend.services.stock_registry import StockRegistryService


class StockRegistryServiceTests(unittest.TestCase):
    def test_registry_contains_multiple_entries(self) -> None:
        service = StockRegistryService()
        registry = service.get_registry(limit=5)
        self.assertEqual(len(registry), 5)
        self.assertTrue(all("symbol" in entry for entry in registry))

    def test_single_symbol_lookup(self) -> None:
        service = StockRegistryService()
        entry = service.get_symbol("THYAO")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["symbol"], "THYAO")
        self.assertIn("listing_status", entry)


if __name__ == "__main__":
    unittest.main()
