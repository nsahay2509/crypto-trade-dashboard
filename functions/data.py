

# functions/data.py

import os
import requests
from datetime import datetime

# --- Logging ---
LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "trade.log")

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("")

def log_and_print(message):
    """Logs message to file and prints it to the console."""
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(f"{message}\n")
        f.flush()

def log_debug(message):
    """Use this for quieter debug logs, if needed."""
    with open(LOG_FILE, "a") as f:
        f.write(f"[DEBUG] {message}\n")
        f.flush()

# --- API Fetching ---
BASE_URL = "https://cdn.india.deltaex.org/v2/tickers"

def fetch_data(symbol):
    """Fetch data from the Delta Exchange API for a given symbol."""
    try:
        response = requests.get(f"{BASE_URL}/{symbol}")
        if response.status_code == 200:
            return response.json().get("result", {})
        return {}
    except Exception as e:
        log_debug(f"Fetch Error: {e}")
        return {}
