

# functions/logic.py

from constants import RSI_HIGH_LEVEL, RSI_LOW_LEVEL

def check_entry_criteria(price, ema, macd, signal, rsi, vwap,
                          use_ema=True, use_macd=True, use_rsi=True, use_vwap=True):
    """
    Evaluates all indicators and determines if it's a BUY, SELL, or HOLD signal.

    Returns:
        (signal: str, criteria: dict)
        - signal: "BUY", "SELL", or "HOLD"
        - criteria: dictionary with indicator evaluations
    """
    long_criteria = {}
    short_criteria = {}

    # ---- LONG (BUY) Conditions ----
    if use_ema:
        long_criteria["EMA"] = price > ema if ema is not None else False
    if use_macd:
        long_criteria["MACD"] = macd > signal if macd is not None and signal is not None else False
    if use_rsi:
        long_criteria["RSI"] = rsi > RSI_HIGH_LEVEL if rsi is not None else False
    if use_vwap:
        long_criteria["VWAP"] = price > vwap if vwap is not None else False

    if all(long_criteria.values()):
        return "BUY", long_criteria

    # ---- SHORT (SELL) Conditions ----
    if use_ema:
        short_criteria["EMA"] = price < ema if ema is not None else False
    if use_macd:
        short_criteria["MACD"] = macd < signal if macd is not None and signal is not None else False
    if use_rsi:
        short_criteria["RSI"] = rsi < RSI_LOW_LEVEL if rsi is not None else False
    if use_vwap:
        short_criteria["VWAP"] = price < vwap if vwap is not None else False

    if all(short_criteria.values()):
        return "SELL", short_criteria

    return "HOLD", long_criteria  # return long_criteria as default for inspection
