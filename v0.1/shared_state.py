import threading

# Shared state for telemetry and GPS data
telemetry_lock = threading.Lock()
telemetry_latest = {"telemetry": None, "gps": None, "sync": None}

history = {
    "temp": [],
    "pre": [],
    "hum": [],
    "alt": [],
    "rss": [],  # regular RSSI
    "ack_rss": []  # ACK RSSI
}

gps_history = {"lat": [], "lon": [], "alt": [], "sats": []}

MAX_POINTS = 100  # Nombre maximum de points affichés
