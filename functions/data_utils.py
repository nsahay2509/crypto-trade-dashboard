

import json
from datetime import datetime

def write_state_file(state_dict, path="state.json"):
    """
    Safely writes the bot's state to a JSON file.
    """
    state_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(path, "w") as f:
            json.dump(state_dict, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Could not write to state file: {e}")

