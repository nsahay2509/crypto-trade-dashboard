# j1.py

import time
import pandas as pd
import numpy as np
from functions.data_utils import write_state_file
from datetime import datetime, timedelta
import warnings

# Suppress warnings
warnings.simplefilter("ignore")

# ---- Imports ----
from constants import *
from functions.data import fetch_data, log_and_print, log_debug
from functions.indicators import calculate_ema, calculate_macd, calculate_rsi, calculate_vwap
from functions.utils import apply_delay, normalize_indicators
from functions.trade_logic import enter_trade, exit_trade, finalize_exit
from functions.logic import check_entry_criteria


# ---- Initialize ----
prices = []
position = None
entry_price = None
entry_time = None
total_profit = 0
extreme_price = None  # highest for long, lowest for short
trade_no = 1

trade_df = pd.DataFrame(columns=[
    "Trade No", "Trade Type", "Entry Date", "Entry Time", "Entry Price",
    "Exit Date", "Exit Time", "Exit Price", "Trade Fee", "Profit", "Total Profit",
    "Take Profit Percentage", "Stop Loss Percentage", "Trailing Trigger Percentage",
    "Trailing Margin Percentage", "Trade Cost Percentage"
])

vwap_prices = []
vwap_volumes = []

# ---- Main Loop ----
while True:
    data = fetch_data(SYMBOL)
    if not data:
        apply_delay(position, PAUSE_AFTER_ENTRY, PAUSE_AFTER_EXIT)
        continue

    # Timestamp conversion
    timestamp = int(str(data["timestamp"])[:10])
    utc_time = datetime.utcfromtimestamp(timestamp)
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    formatted_time = ist_time.strftime('%Y-%m-%d %H:%M:%S')

    # Extract price and volume
    price = float(data.get("close", 0))
    volume = float(data.get("volume", 0))
    log_debug(f"🕒 {formatted_time} | Watching price: ${price:.2f}")


    # Update price list
    prices.append(price)
    if len(prices) > 26:
        prices.pop(0)

    # Indicators
    # ---- Indicators ----
    ema = calculate_ema(prices) if USE_EMA else None
    macd, signal = calculate_macd(prices) if USE_MACD else (None, None)
    rsi = calculate_rsi(prices) if USE_RSI else None
    vwap = calculate_vwap(price, volume) if USE_VWAP else None

    # ---- Normalize all indicator values ----
    ema, macd, signal, rsi, vwap = normalize_indicators(
        ema=ema, macd=macd, signal=signal, rsi=rsi, vwap=vwap
    ).values()


    # ---- Entry Logic ----
    if position is None:
        signal, criteria = check_entry_criteria(
            price, ema, macd, signal, rsi, vwap,
            USE_EMA, USE_MACD, USE_RSI, USE_VWAP
        )

        if signal == "BUY":
            log_and_print(f"📈 BUY SIGNAL | {formatted_time} | {criteria}")
            position, entry_price, entry_time, extreme_price, entry_df = enter_trade(
                price, formatted_time, trade_no, "LONG",
                TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT,
                TRAILING_TRIGGER_PERCENT, TRAILING_MARGIN_PERCENT
            )
            trade_df = pd.concat([trade_df, entry_df], ignore_index=True)
            trade_df.to_excel(EXCEL_PATH, index=False)
            total_profit = 0

        elif signal == "SELL":
            log_and_print(f"📉 SELL SIGNAL | {formatted_time} | {criteria}")
            position, entry_price, entry_time, extreme_price, entry_df = enter_trade(
                price, formatted_time, trade_no, "SHORT",
                TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT,
                TRAILING_TRIGGER_PERCENT, TRAILING_MARGIN_PERCENT
            )
            trade_df = pd.concat([trade_df, entry_df], ignore_index=True)
            trade_df.to_excel(EXCEL_PATH, index=False)
            total_profit = 0


    # ---- Exit Logic ----
    elif position in ["LONG", "SHORT"]:
        price_diff = (price - entry_price) if position == "LONG" else (entry_price - price)
        current_pnl = price_diff * TRADE_SIZE
        pnl_percent = (price_diff / entry_price) * 100

        log_and_print(f"📢 {formatted_time} | Price: ${price:.2f} | P&L: ${current_pnl:.2f} ({pnl_percent:+.2f}%)")
        log_debug(f"[LIVE P&L] {formatted_time} | {position} | Price=${price:.2f} | P&L=${current_pnl:.2f} ({pnl_percent:+.2f}%)")


        position, total_profit, extreme_price, exit_msg = exit_trade(
            price, entry_price, position, extreme_price, total_profit,
            TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT,
            TRAILING_TRIGGER_PERCENT, TRAILING_MARGIN_PERCENT
        )

        if exit_msg:
            log_and_print(exit_msg)
            log_and_print(f"📊 Total Profit: ${total_profit:.2f}")

            trade_df = finalize_exit(
                trade_df, trade_no, price, formatted_time, entry_price, total_profit
            )
            trade_df.to_excel(EXCEL_PATH, index=False)

            position = None
            trade_no += 1
            time.sleep(PAUSE_AFTER_EACH_TRADE)

    # ---- Write State to File ----

    # Compute current P&L if a trade is active
    current_pnl = (
        (price - entry_price) * TRADE_SIZE if position == "LONG"
        else (entry_price - price) * TRADE_SIZE if position == "SHORT"
        else 0
    )
    current_pnl_pct = (
        ((price - entry_price) / entry_price * 100) if position == "LONG"
        else ((entry_price - price) / entry_price * 100) if position == "SHORT"
        else 0
    )

    # Build state
    state = {
        "bot_status": "RUNNING" if position else "IDLE",
        "current_price": price,
        "position": {
            "active": bool(position),
            "trade_no": trade_no,
            "type": position,
            "entry_price": entry_price,
            "stop_loss": entry_price * (1 - STOP_LOSS_PERCENT) if position == "LONG"
                        else entry_price * (1 + STOP_LOSS_PERCENT) if position == "SHORT"
                        else None,
            "take_profit": entry_price * (1 + TAKE_PROFIT_PERCENT) if position == "LONG"
                        else entry_price * (1 - TAKE_PROFIT_PERCENT) if position == "SHORT"
                        else None,
            "trailing_stop": extreme_price * (1 - TRAILING_MARGIN_PERCENT) if position == "LONG"
                            else extreme_price * (1 + TRAILING_MARGIN_PERCENT) if position == "SHORT"
                            else None,
            "entry_time": entry_time,
            "duration": "",  # You can later add this
            "pnl": round(current_pnl, 2),
            "pnl_percent": round(current_pnl_pct, 2)
        } if position else {},
        "indicators": {
            "EMA": {
                "value": round(ema, 2) if isinstance(ema, (int, float)) else None,
                "used": USE_EMA,
                "signal": (
                    "BUY" if isinstance(ema, (int, float)) and price > ema
                    else "SELL" if isinstance(ema, (int, float)) and price < ema
                    else "HOLD"
                )
            },
            "MACD": {
                "value": round(macd, 4) if isinstance(macd, (int, float)) else None,
                "used": USE_MACD,
                "signal": (
                    "BUY" if isinstance(macd, (int, float)) and isinstance(signal, (int, float)) and macd > signal
                    else "SELL" if isinstance(macd, (int, float)) and isinstance(signal, (int, float)) and macd < signal
                    else "HOLD"
                )
            },
            "RSI": {
                "value": round(rsi, 2) if isinstance(rsi, (int, float)) else None,
                "used": USE_RSI,
                "signal": (
                    "BUY" if isinstance(rsi, (int, float)) and rsi > RSI_HIGH_LEVEL
                    else "SELL" if isinstance(rsi, (int, float)) and rsi < RSI_LOW_LEVEL
                    else "HOLD"
                )
            },
            "VWAP": {
                "value": round(vwap, 2) if isinstance(vwap, (int, float)) else None,
                "used": USE_VWAP,
                "signal": (
                    "BUY" if isinstance(vwap, (int, float)) and price > vwap
                    else "SELL" if isinstance(vwap, (int, float)) and price < vwap
                    else "HOLD"
                )
            },
        },

        "logs": []  # Optional for now, or append from a rolling buffer
    }

    # Write to JSON
    write_state_file(state)


    # ---- Sleep Before Next Iteration ----
    apply_delay(position, PAUSE_AFTER_ENTRY, PAUSE_AFTER_EXIT)
