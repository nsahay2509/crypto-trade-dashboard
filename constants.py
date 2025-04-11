
# constants.py

# constants.py

# --- Trade Parameters ---
TAKE_PROFIT_PERCENT = 0.02         # 2% target
STOP_LOSS_PERCENT = 0.005          # 0.5% max loss
TRAILING_TRIGGER_PERCENT = 0.002   # 0.2% increase needed to update trailing stop
TRAILING_MARGIN_PERCENT = 0.005    # 0.5% from the highest/lowest price

# --- Sleep Timers (in seconds) ---
PAUSE_AFTER_EACH_TRADE = 20        # After full trade
PAUSE_AFTER_ENTRY = 5              # When waiting for entry
PAUSE_AFTER_EXIT = 8               # After exiting but still in the loop

# --- Fees ---
TRADE_COST_PERCENT = 0.0005        # 0.05% fee rate
GST_RATE = 0.18                    # 18% GST on trade fee

# --- Lot Information ---
LOT_SIZE = 100                     # Total units per lot
LOTS_PER_CRYPTO = 1000            # How many lots per crypto unit
TRADE_SIZE = LOT_SIZE / LOTS_PER_CRYPTO  # Used in P&L calculation

# --- Indicator Controls ---
USE_EMA = True
USE_MACD = True
USE_RSI = True
USE_VWAP = True

# --- RSI Custom Thresholds ---
RSI_HIGH_LEVEL = 0.6
RSI_LOW_LEVEL = 0.4

# --- Others ---
SYMBOL = "BTCUSD"
EXCEL_PATH = "logs/trades.xlsx"
