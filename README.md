### Overview:

A super simple stock market system for the Global Beverage Corporation Exchange (GBCE), focused on trading stocks for beverage companies. It's a small, early-phase part of the system that handles just the essentials.

What it does:

    For each stock:
        Calculate the Dividend Yield based on its price.
        Calculate the P/E Ratio based on its price.
        Record trades with details like time, quantity, whether it's a buy or sell, and the price.
        Calculate the Volume Weighted Stock Price (VWSP) using trades from the last 5 minutes.

    For the whole exchange:
        Calculate the GBCE All Share Index, which averages the VWSPs from all stocks.

### Limitations:

    All data is stored in memory—no databases or files.
    Focuses only on the basic calculations, keeping things simple with no extra features.
