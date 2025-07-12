# src/config.py
import os

HIGH    = float(os.getenv("THRESHOLD_HIGH", 0.70))
MEDIUM  = float(os.getenv("THRESHOLD_MEDIUM", 0.30))
ALERT_CHANNELS = ["email", "slack"]
