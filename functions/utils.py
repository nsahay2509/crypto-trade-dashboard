

# functions/utils.py

import time
from constants import GST_RATE

def apply_delay(position, pause_after_entry, pause_after_exit):
    """Applies appropriate delay depending on whether trade is open."""
    if position is None:
        time.sleep(pause_after_entry)
    else:
        time.sleep(pause_after_exit)

def calculate_total_fees(entry_price, exit_price, lot_size, lots_per_crypto, fee_rate=0.0005, gst_rate=GST_RATE):
    """
    Calculate trading fees including GST for entry and exit.
    """
    total_notional_price = entry_price + exit_price
    gross_fee = total_notional_price * fee_rate * lot_size / lots_per_crypto
    total_fees = gross_fee * (1 + gst_rate)
    return total_fees

# functions/utils.py

def normalize_indicators(**kwargs):
    """
    Converts any numpy.generic or numpy.ndarray indicator values to Python float.
    Args:
        kwargs: keyword arguments of indicators, e.g., ema=..., rsi=...
    Returns:
        dict with same keys and float values (or untouched if already native types)
    """
    import numpy as np

    normalized = {}
    for key, val in kwargs.items():
        if isinstance(val, (np.generic, np.ndarray)):
            normalized[key] = float(val)
        else:
            normalized[key] = val
    return normalized
