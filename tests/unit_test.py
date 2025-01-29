import pytest
from datetime import datetime, timedelta
from unittest import mock
import math
from freezegun import freeze_time
import sys
print(sys.path)

from src.domain import Trade,DomainError
from src.stock import Stock
from src.stock_market import StockMarket
from config import TRADE_TIME_WINDOW

# Tests for Stock class

def test_create_common_stock_with_fixed_dividend_raises_error():
    with pytest.raises(DomainError):
        Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=0.05, par_value=100)

def test_create_preferred_stock_without_fixed_dividend_raises_error():
    with pytest.raises(DomainError):
        Stock(symbol="GIN", type="Preferred", last_dividend=8, fixed_dividend=None, par_value=100)

def test_negative_last_dividend_raises_error():
    with pytest.raises(DomainError):
        Stock(symbol="TEA", type="Common", last_dividend=-5, fixed_dividend=None, par_value=100)

def test_non_positive_par_value_raises_error():
    with pytest.raises(DomainError):
        Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=0)

def test_preferred_stock_fixed_dividend_outside_range_raises_error():
    with pytest.raises(DomainError):
        Stock(symbol="GIN", type="Preferred", last_dividend=8, fixed_dividend=1.5, par_value=100)
    with pytest.raises(DomainError):
        Stock(symbol="GIN", type="Preferred", last_dividend=8, fixed_dividend=-0.1, par_value=100)

def test_dividend_yield_common():
    stock = Stock(symbol="POP", type="Common", last_dividend=8, fixed_dividend=None, par_value=100)
    assert stock.calculate_dividend_yield(100) == 0.08

def test_dividend_yield_preferred():
    stock = Stock(symbol="GIN", type="Preferred", last_dividend=8, fixed_dividend=0.02, par_value=100)
    assert stock.calculate_dividend_yield(100) == (0.02 * 100) / 100

def test_dividend_yield_zero_price_raises_error():
    stock = Stock(symbol="ALE", type="Common", last_dividend=5, fixed_dividend=None, par_value=100)
    with pytest.raises(DomainError):
        stock.calculate_dividend_yield(0)

def test_pe_ratio_common():
    stock = Stock(symbol="ALE", type="Common", last_dividend=5, fixed_dividend=None, par_value=100)
    assert stock.calculate_pe_ratio(100) == 20.0

def test_pe_ratio_preferred():
    stock = Stock(symbol="GIN", type="Preferred", last_dividend=0, fixed_dividend=0.02, par_value=100)
    assert stock.calculate_pe_ratio(10) == 10 / (0.02 * 100)

def test_pe_ratio_zero_dividend_raises_error():
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    with pytest.raises(DomainError):
        stock.calculate_pe_ratio(100)

def test_record_trade_valid():
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    stock.record_trade(100, True, 50)
    assert len(stock._trades) == 1
    trade = stock._trades[0]
    assert trade.quantity == 100
    assert trade.is_buy is True
    assert trade.price == 50

def test_record_trade_negative_quantity_raises_error():
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    with pytest.raises(DomainError):
        stock.record_trade(-100, True, 50)

def test_record_trade_zero_price_raises_error():
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    with pytest.raises(DomainError):
        stock.record_trade(100, True, 0)

@freeze_time("2023-01-01 12:00:00")
def test_volume_weighted_price():
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    with freeze_time("2023-01-01 11:55:00"):
        stock.record_trade(100, True, 10)
    with freeze_time("2023-01-01 11:57:00"):
        stock.record_trade(200, True, 15)
    with freeze_time("2023-01-01 11:54:59"):
        stock.record_trade(50, True, 5)
    vwp = stock.calculate_volume_weighted_price()
    expected = (100 * 10 + 200 * 15) / (100 + 200)
    assert vwp == pytest.approx(expected)

def test_volume_weighted_price_no_trades():
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    assert stock.calculate_volume_weighted_price() == 0.0

# Tests for StockMarket class

def test_add_stock():
    market = StockMarket()
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    market.add_stock(stock)
    assert market.get_stock("TEA") is stock

def test_add_duplicate_stock_raises_error():
    market = StockMarket()
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    market.add_stock(stock)
    with pytest.raises(DomainError):
        market.add_stock(stock)

def test_get_nonexistent_stock_returns_none():
    market = StockMarket()
    assert market.get_stock("INVALID") is None

def test_all_share_index_single_stock():
    market = StockMarket()
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    market.add_stock(stock)
    with mock.patch.object(stock, 'calculate_volume_weighted_price', return_value=100.0):
        assert market.calculate_all_share_index() == pytest.approx(100.0)

def test_all_share_index_multiple_stocks():
    market = StockMarket()
    stock1 = Stock(symbol="A", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    stock2 = Stock(symbol="B", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    market.add_stock(stock1)
    market.add_stock(stock2)
    with mock.patch.object(stock1, 'calculate_volume_weighted_price', return_value=2.0), \
         mock.patch.object(stock2, 'calculate_volume_weighted_price', return_value=8.0):
        expected = math.sqrt(2 * 8)
        assert market.calculate_all_share_index() == pytest.approx(expected)

def test_all_share_index_no_valid_prices_returns_zero():
    market = StockMarket()
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    market.add_stock(stock)
    with mock.patch.object(stock, 'calculate_volume_weighted_price', return_value=0.0):
        assert market.calculate_all_share_index() == 0.0

@freeze_time("2023-01-01 12:00:00")
def test_all_share_index_integration():
    market = StockMarket()
    stock1 = Stock(symbol="A", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    stock2 = Stock(symbol="B", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    market.add_stock(stock1)
    market.add_stock(stock2)
    with freeze_time("2023-01-01 11:59:00"):
        stock1.record_trade(100, True, 10)
    stock2.record_trade(200, True, 20)
    expected = math.sqrt(10 * 20)
    assert market.calculate_all_share_index() == pytest.approx(expected)

def test_all_share_index_overflow():
    market = StockMarket()
    stock = Stock(symbol="TEA", type="Common", last_dividend=0, fixed_dividend=None, par_value=100)
    market.add_stock(stock)
    with mock.patch.object(stock, 'calculate_volume_weighted_price', return_value=1e308):
        with mock.patch('math.exp', side_effect=OverflowError):
            assert market.calculate_all_share_index() == 0.0

# Test Trade dataclass

def test_trade_creation():
    timestamp = datetime.now()
    trade = Trade(timestamp=timestamp, quantity=100, is_buy=True, price=50)
    assert trade.timestamp == timestamp
    assert trade.quantity == 100
    assert trade.is_buy is True
    assert trade.price == 50
