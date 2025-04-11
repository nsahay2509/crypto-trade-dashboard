# dashboard.py

import streamlit as st
import json
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

STATE_FILE = Path("state.json")

st.set_page_config(page_title="Trading Bot Dashboard", layout="wide")
st.title("📊 Real-Time Trade Monitor")

# ✅ Native Streamlit auto-refresh every 3 seconds without flicker
st_autorefresh(interval=3000, limit=None, key="refresh")

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

state = load_state()

# === TOP PANEL ===
col1, col2, col3 = st.columns(3)
col1.metric("📉 Current Price", f"${state.get('current_price', 0):,.2f}")
col2.metric("📌 Bot Status", state.get("bot_status", "N/A"))
col3.metric("📅 Updated At", state.get("timestamp", "N/A"))

# === INDICATORS PANEL ===
st.subheader("📟 Indicator Signals")
indicators = state.get("indicators", {})

cols = st.columns(4)
for i, (name, data) in enumerate(indicators.items()):
    value = data.get("value")
    signal = data.get("signal")
    used = data.get("used")

    # Define custom signal label with color
    if signal == "BUY":
        signal_text = ":green[BUY]"
    elif signal == "SELL":
        signal_text = ":red[SELL]"
    else:
        signal_text = ""  # HOLD → show nothing

    with cols[i]:
        st.markdown(f"**{name} {'✅' if used else '❌'}**")
        st.metric(
            label="",
            value=f"{value}" if value is not None else "N/A"
        )
        if signal_text:
            st.markdown(f"{signal_text}")


# === POSITION PANEL ===
position = state.get("position", {})
if position.get("active"):
    st.subheader("📈 Active Trade")
    st.code(f"{position['type']} | Entry: ${position['entry_price']} | P&L: ${position['pnl']} ({position['pnl_percent']}%)")

    pos1, pos2, pos3 = st.columns(3)
    pos1.metric("🎯 Take Profit", f"${position['take_profit']:.2f}")
    pos2.metric("🛑 Stop Loss", f"${position['stop_loss']:.2f}")
    pos3.metric("📐 Trailing SL", f"${position['trailing_stop']:.2f}")
else:
    st.subheader("💤 No Active Trade")

# st.markdown("---")
# st.caption("Bot Dashboard | Updates every 3 seconds without flicker ✨")
