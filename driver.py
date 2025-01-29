from src.stock import Stock
from src.stock_market import StockMarket

if __name__ == "__main__":
    # Initialize market with sample data
    market = StockMarket()
    market.add_stock(Stock("TEA", "Common", 0, None, 100))
    market.add_stock(Stock("POP", "Common", 8, None, 100))
    market.add_stock(Stock("GIN", "Preferred", 8, 0.02, 100))
    
    # Simulate trades
    gin = market.get_stock("GIN")
    if gin:
        gin.record_trade(100, True, 150)
        gin.record_trade(200, False, 155)
    else:
        logger.error("GIN stock not found")
    
    # Calculate metrics
    print(f"GBCE All Share Index: {market.calculate_all_share_index():.2f}")
