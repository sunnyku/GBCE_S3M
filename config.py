import os
import logging

# Volume Weighted Stock Price based on trades in past 5 minutes
TRADE_TIME_WINDOW = int(os.getenv("TRADE_TIME_WINDOW_MINUTES", "5"))
# Just to prevent memory leaks
MAX_TRADE_HISTORY = int(os.getenv("MAX_TRADE_HISTORY", "10000"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
