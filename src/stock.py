from datetime import datetime, timedelta
import threading
from typing import Deque, Optional
from collections import deque

from config import TRADE_TIME_WINDOW, MAX_TRADE_HISTORY
from config import logger
from .domain import Trade, DomainError
import pdb

class Stock:
    """Represents a stock with trade recording and utils for financial metrics."""

    def __init__(self, symbol: str, type: str, last_dividend: float,
                 fixed_dividend: Optional[float], par_value: float):
        if type not in ("Common", "Preferred"):
            raise DomainError(f"Invalid stock type: {type}")
        if last_dividend < 0:
            raise DomainError("Last dividend should be positive")
        if par_value <= 0:
            raise DomainError("Par value should be positive")
        if type == "Common" and fixed_dividend is not None:
            raise DomainError("Common stock should not have a fixed dividend")
        if type == "Preferred" and fixed_dividend is None:
            raise DomainError("Preferred stocks should have a fixed dividend")
        if fixed_dividend is not None and (fixed_dividend < 0 or fixed_dividend > 1):
            raise DomainError("Fixed dividend must be between 0 and 1")

        self.symbol = symbol
        self.type = type
        self.last_dividend = last_dividend
        self.fixed_dividend = fixed_dividend
        self.par_value = par_value
        self._trades: Deque[Trade] = deque(maxlen=MAX_TRADE_HISTORY)
        self._lock = threading.Lock()  # Thread safety for trade recording

    def calculate_dividend_yield(self, price: float) -> float:
        """Given any price as input, calculate the dividend yield"""
        if price <= 0:
            raise DomainError("Price should be greater than zero")

        if self.type == "Common":
            return self.last_dividend / price
        else:  # Preferred
            return (self.fixed_dividend * self.par_value) / price

    def calculate_pe_ratio(self, price: float) -> float:
        """Given any price as input, calculate the P/E Ratio"""
        if price <= 0:
            raise DomainError("Price should be greater than zero")

        dividend = (
            self.last_dividend
            if self.type == "Common"
            else (self.fixed_dividend * self.par_value)
        )
        if dividend <= 0:
            raise DomainError("Dividend should be positive for P/E ratio calculation")

        return price / dividend

    def record_trade(self, quantity: int, is_buy: bool, price: float) -> None:
        """
        Record a trade, with timestamp, quantity, buy or sell indicator and price
        """
        if quantity <= 0:
            raise DomainError("Trade quantity should be positive")
        if price <= 0:
            raise DomainError("Trade price should be positive")

        trade = Trade(datetime.now(), quantity, is_buy, price)
        with self._lock:  # Thread-safe write
            self._trades.append(trade)
        logger.info(f"Recorded trade: {trade}")
        pdb.set_trace()

    def calculate_volume_weighted_price(self) -> float:
        """Calculate volume-weighted stock price for trades within the time window"""
        cutoff_time = datetime.now() - timedelta(minutes=TRADE_TIME_WINDOW)

        with self._lock:  # Thread-safe read
            recent_trades = [t for t in self._trades if t.timestamp >= cutoff_time]

        if not recent_trades:
            logger.warning(f"No trades for {self.symbol} in the last {TRADE_TIME_WINDOW} minutes")
            return 0.0

        total_value = sum(t.price * t.quantity for t in recent_trades)
        total_quantity = sum(t.quantity for t in recent_trades)
        return total_value / total_quantity
