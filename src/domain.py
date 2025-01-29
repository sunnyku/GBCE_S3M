from dataclasses import dataclass
from datetime import datetime

class DomainError(Exception):
    """Base exception for domain-specific errors."""
    pass

@dataclass(frozen=True)
class Trade:
    timestamp: datetime
    quantity: int
    is_buy: bool
    price: float
