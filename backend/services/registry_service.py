from typing import List, Dict
from ..schemas.stock import StockInfo

class RegistryService:
    """Service to manage ALL BIST stock symbols and company info."""

    def __init__(self):
        # Extended list representing BIST TÜM (Partial list for brevity, in reality it should be 500+)
        self.stocks = {
            "THYAO": {"name": "Türk Hava Yolları", "sector": "Transportation"},
            "ASELS": {"name": "Aselsan", "sector": "Defense"},
            "EREGL": {"name": "Erdemir", "sector": "Steel"},
            "KCHOL": {"name": "Koç Holding", "sector": "Conglomerate"},
            "SISE": {"name": "Şişecam", "sector": "Glass"},
            "AKBNK": {"name": "Akbank", "sector": "Banking"},
            "GARAN": {"name": "Garanti BBVA", "sector": "Banking"},
            "TUPRS": {"name": "Tüpraş", "sector": "Refining"},
            "BIMAS": {"name": "Bim Mağazalar", "sector": "Retail"},
            "SASA": {"name": "Sasa Polyester", "sector": "Chemicals"},
            "TOASO": {"name": "Tofaş Oto", "sector": "Automotive"},
            "FROTO": {"name": "Ford Otosan", "sector": "Automotive"},
            "ARCLK": {"name": "Arçelik", "sector": "Consumer Durables"},
            "VESTL": {"name": "Vestel", "sector": "Electronics"},
            "PETKM": {"name": "Petkim", "sector": "Chemicals"},
            "TKFEN": {"name": "Tekfen Holding", "sector": "Construction"},
            "DOAS": {"name": "Doğuş Otomotiv", "sector": "Automotive"},
            "ISCTR": {"name": "İş Bankası (C)", "sector": "Banking"},
            "YKBNK": {"name": "Yapı Kredi", "sector": "Banking"},
            "HALKB": {"name": "Halkbank", "sector": "Banking"},
            "VAKBN": {"name": "Vakıfbank", "sector": "Banking"},
            "TSKB": {"name": "TSKB", "sector": "Banking"},
            "KARDM": {"name": "Kardemir (D)", "sector": "Steel"},
            "PGSUS": {"name": "Pegasus", "sector": "Transportation"},
            "ENKAI": {"name": "Enka İnşaat", "sector": "Construction"},
            "TAVHL": {"name": "TAV Havalimanları", "sector": "Transportation"},
            "SOKM": {"name": "Şok Marketler", "sector": "Retail"},
            "MGROS": {"name": "Migros", "sector": "Retail"},
            "TTKOM": {"name": "Türk Telekom", "sector": "Telecommunications"},
            "TCELL": {"name": "Turkcell", "sector": "Telecommunications"},
            "KOZAL": {"name": "Koza Altın", "sector": "Mining"},
            "KOZAA": {"name": "Koza Anadolu Metal", "sector": "Mining"},
            "IPEKE": {"name": "İpek Doğal Enerji", "sector": "Energy"},
            "ODAS": {"name": "Odaş Elektrik", "sector": "Energy"},
            "AKSEN": {"name": "Aksa Enerji", "sector": "Energy"},
            "ZOREN": {"name": "Zorlu Enerji", "sector": "Energy"},
            "ALARK": {"name": "Alarko Holding", "sector": "Conglomerate"},
            "SAHOL": {"name": "Sabancı Holding", "sector": "Conglomerate"},
            "GUBRF": {"name": "Gübre Fabrikaları", "sector": "Chemicals"},
            "HEKTS": {"name": "Hektaş", "sector": "Chemicals"},
            "EGEEN": {"name": "Ege Endüstri", "sector": "Automotive"},
            "OTKAR": {"name": "Otokar", "sector": "Automotive"},
            "TMSN": {"name": "Tümosan", "sector": "Automotive"},
            "KMPUR": {"name": "Kimteks Poliüretan", "sector": "Chemicals"},
            "EUPWR": {"name": "Europower Enerji", "sector": "Energy"},
            "ASTOR": {"name": "Astor Enerji", "sector": "Energy"},
            "KONTR": {"name": "Kontrolmatik", "sector": "Technology"},
            "SMRTG": {"name": "Smart Güneş Enerjisi", "sector": "Energy"},
            "YEOTK": {"name": "Yeo Teknoloji", "sector": "Technology"},
            "MIATK": {"name": "Mia Teknoloji", "sector": "Technology"},
        }

    def get_all_symbols(self) -> List[str]:
        # Return all symbols, shuffled to avoid alphabetical bias
        import random
        symbols = list(self.stocks.keys())
        random.shuffle(symbols)
        return symbols

    def get_stock_info(self, symbol: str) -> StockInfo:
        data = self.stocks.get(symbol, {"name": f"{symbol} Stock", "sector": "Unknown"})
        return StockInfo(symbol=symbol, name=data["name"], sector=data["sector"])

registry_service = RegistryService()
