

# functions/indicators.py

import pandas as pd
import numpy as np

# Exponential Moving Average
def calculate_ema(prices, N=20):
    if len(prices) < N:
        return None
    K = 2 / (N + 1)
    ema = sum(prices[:N]) / N
    for price in prices[N:]:
        ema = (price * K) + (ema * (1 - K))
    return ema

# MACD and Signal Line
def calculate_macd(prices):
    if len(prices) < 26:
        return None, None
    short_ema = calculate_ema(prices, N=12)
    long_ema = calculate_ema(prices, N=26)
    if short_ema is None or long_ema is None:
        return None, None
    macd = short_ema - long_ema

    if not hasattr(calculate_macd, "macd_history"):
        calculate_macd.macd_history = []
    calculate_macd.macd_history.append(macd)
    if len(calculate_macd.macd_history) > 9:
        calculate_macd.macd_history.pop(0)

    signal_line = calculate_ema(calculate_macd.macd_history, N=9)
    return macd, signal_line

# RSI
def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return None
    df = pd.DataFrame(prices, columns=["Close"])
    df["Change"] = df["Close"].diff()
    df["Gain"] = np.where(df["Change"] > 0, df["Change"], 0)
    df["Loss"] = np.where(df["Change"] < 0, -df["Change"], 0)
    avg_gain = df["Gain"].rolling(window=period, min_periods=1).mean()
    avg_loss = df["Loss"].rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs)).iloc[-1]

# VWAP
vwap_prices = []
vwap_volumes = []

def calculate_vwap(price, volume, N=20):
    if volume > 0:
        vwap_prices.append(price * volume)
        vwap_volumes.append(volume)
    if len(vwap_prices) > N:
        vwap_prices.pop(0)
        vwap_volumes.pop(0)
    return sum(vwap_prices) / sum(vwap_volumes) if sum(vwap_volumes) > 0 else None
