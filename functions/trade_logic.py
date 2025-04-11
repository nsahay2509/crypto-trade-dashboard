


# functions/trade_logic.py

import pandas as pd
from functions.data import log_and_print, log_debug
from functions.utils import calculate_total_fees
from constants import TRADE_COST_PERCENT, LOT_SIZE, LOTS_PER_CRYPTO, TRADE_SIZE

# ========== Entry Functions ==========

def enter_trade(price, formatted_time, trade_no, direction, take_profit, stop_loss, trailing_trigger, trailing_margin):
    """
    Entry logic for either long or short position.
    """
    entry_price = price
    entry_time = formatted_time
    extreme_price = price  # highest for long, lowest for short
    stop = entry_price * (1 - stop_loss) if direction == "LONG" else entry_price * (1 + stop_loss)

    log_and_print(f"\n🟢 ENTER {direction}: {formatted_time} | Entry Price=${entry_price:.2f} | Stop Loss=${stop:.2f}")

    entry_df = pd.DataFrame([{
        'Trade No': trade_no,
        'Trade Type': direction.title(),
        'Entry Date': entry_time.split(' ')[0],
        'Entry Time': entry_time.split(' ')[1],
        'Entry Price': entry_price,
        'Exit Date': None,
        'Exit Time': None,
        'Exit Price': None,
        'Trade Fee': None,
        'Profit': None,
        'Total Profit': 0,
        'Take Profit Percentage': take_profit,
        'Stop Loss Percentage': stop_loss,
        'Trailing Trigger Percentage': trailing_trigger,
        'Trailing Margin Percentage': trailing_margin,
        'Trade Cost Percentage': TRADE_COST_PERCENT
    }])

    return direction, entry_price, entry_time, extreme_price, entry_df

# ========== Exit Logic ==========

def exit_trade(price, entry_price, position, extreme_price, total_profit,
               take_profit, stop_loss, trailing_trigger, trailing_margin):
    """
    Generalized exit logic for long and short positions.
    
    Returns:
        position, total_profit, updated_extreme_price, exit_message (or None if no exit)
    """
    is_long = position == "LONG"

    # --- Exit levels ---
    tp_level = entry_price * (1 + take_profit) if is_long else entry_price * (1 - take_profit)
    sl_level = entry_price * (1 - stop_loss) if is_long else entry_price * (1 + stop_loss)
    new_extreme = extreme_price

    # --- Trailing Stop Update ---
    if is_long and price > extreme_price:
        delta = (price - extreme_price) / extreme_price
        proposed_trailing = price * (1 - trailing_margin)
        if delta >= trailing_trigger and proposed_trailing > sl_level:
            old = extreme_price
            new_extreme = price
            trailing_level = new_extreme * (1 - trailing_margin)
            log_and_print(f"🔄 LONG Trailing updated: {old:.2f} → {new_extreme:.2f} | Stop: {trailing_level:.2f}")
            log_debug(
                f"[TRAILING SL] LONG: Highest {old:.2f} → {new_extreme:.2f}, "
                f"SL: {old * (1 - trailing_margin):.2f} → {trailing_level:.2f}"
            )

    elif not is_long and price < extreme_price:
        delta = (extreme_price - price) / extreme_price
        proposed_trailing = price * (1 + trailing_margin)
        if delta >= trailing_trigger and proposed_trailing < sl_level:
            old = extreme_price
            new_extreme = price
            trailing_level = new_extreme * (1 + trailing_margin)
            log_and_print(f"🔄 SHORT Trailing updated: {old:.2f} → {new_extreme:.2f} | Stop: {trailing_level:.2f}")
            log_debug(
                f"[TRAILING SL] SHORT: Lowest {old:.2f} → {new_extreme:.2f}, "
                f"SL: {old * (1 + trailing_margin):.2f} → {trailing_level:.2f}"
            )


    # --- Recalculate trailing level from updated new_extreme ---
    trailing_level = new_extreme * (1 - trailing_margin) if is_long else new_extreme * (1 + trailing_margin)

    # --- Calculate current P&L ---
    profit_calc = (price - entry_price) if is_long else (entry_price - price)

    # --- Exit Conditions ---
    if (is_long and price >= tp_level) or (not is_long and price <= tp_level):
        exit_message = f"🚪 EXIT {position}: Take-profit hit | Profit: ${profit_calc * TRADE_SIZE:.2f}"
        total_profit += profit_calc * TRADE_SIZE
        return None, total_profit, new_extreme, exit_message

    if (is_long and price <= trailing_level) or (not is_long and price >= trailing_level):
        result = "Profit" if profit_calc >= 0 else "Loss"
        exit_message = f"🚪 EXIT {position}: Trailing stop hit | {result}: ${abs(profit_calc * TRADE_SIZE):.2f}"
        total_profit += profit_calc * TRADE_SIZE
        return None, total_profit, new_extreme, exit_message

    if (is_long and price <= sl_level) or (not is_long and price >= sl_level):
        exit_message = f"🚪 EXIT {position}: Stop-loss hit | Loss: ${abs(profit_calc * TRADE_SIZE):.2f}"
        total_profit += profit_calc * TRADE_SIZE
        return None, total_profit, new_extreme, exit_message

    # No exit triggered
    return position, total_profit, new_extreme, None


# ========== Finalize Exit ==========
def finalize_exit(trade_df, trade_no, price, time_str, entry_price, total_profit):
    """
    Handles fee deduction and updates the trade DataFrame.
    """
    trade_fee = calculate_total_fees(entry_price, price, LOT_SIZE, LOTS_PER_CRYPTO, TRADE_COST_PERCENT)
    net_profit = total_profit - trade_fee

    trade_df.loc[trade_df["Trade No"] == trade_no, "Exit Date"] = time_str.split(" ")[0]
    trade_df.loc[trade_df["Trade No"] == trade_no, "Exit Time"] = time_str.split(" ")[1]
    trade_df.loc[trade_df["Trade No"] == trade_no, "Exit Price"] = price
    trade_df.loc[trade_df["Trade No"] == trade_no, "Trade Fee"] = trade_fee
    trade_df.loc[trade_df["Trade No"] == trade_no, "Profit"] = net_profit

    previous_total = (
        trade_df.loc[trade_df["Trade No"] == (trade_no - 1), "Total Profit"].values[0]
        if trade_no > 1 else 0
    )
    trade_df.loc[trade_df["Trade No"] == trade_no, "Total Profit"] = previous_total + net_profit

    return trade_df
