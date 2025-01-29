import threading
import logging
import math
from typing import Dict, Optional

from config import logger
from .domain import DomainError
from .stock import Stock

class StockMarket:
    """Manages all stocks and utils to calculates market-wide indices."""

    def __init__(self):
        self._stocks: Dict[str, Stock] = {}
        self._lock = threading.Lock()

    def add_stock(self, stock: Stock) -> None:
        """Register a new stock symbol in the market."""
        with self._lock:
            if stock.symbol in self._stocks:
                raise DomainError(f"Stock {stock.symbol} already exists")
            self._stocks[stock.symbol] = stock
        logger.info(f"Added stock symbol: {stock.symbol}")

    def get_stock(self, symbol: str) -> Optional[Stock]:
        """Retrieve a stock by symbol."""
        with self._lock:
            return self._stocks.get(symbol)

    def calculate_all_share_index(self) -> float:
        """
        Calculate the GBCE All Share Index using the geometric mean of
        the Volume Weighted Stock Price for all stocks
        """
        with self._lock:
            stocks = list(self._stocks.values())

        vol_w_prices = [stock.calculate_volume_weighted_price() for stock in stocks]
        valid_prices = [p for p in vol_w_prices if p > 0]

        if not valid_prices:
            logger.error("Missing valid prices for All Share Index calculation")
            return 0.0

        try:
            sum_logs = sum(math.log(p) for p in valid_prices)
            geometric_mean = math.exp(sum_logs / len(valid_prices))
        except OverflowError:
            logger.error("Overflow error while calculating geometric mean")
            return 0.0

        return geometric_mean
