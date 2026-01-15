import dearpygui.dearpygui as dpg
import random
import time
import test_3_base_ui
import test_3_left_menu
import test_3_b_graphs
import threading
import json
import socketserver
from http.server import SimpleHTTPRequestHandler
import webbrowser
import serial
import re
from serial_reader import SerialReader
from http_server import start_http_server
from graph_update import update_graph, toggle_source, change_update_interval, clear_graphs, save_data, manual_update
from ui_setup import setup_interface

# Configuration for the HTTP server and map
HTTP_PORT = 8007

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

# Shared state for telemetry and GPS data
telemetry_lock = threading.Lock()
telemetry_latest = {"telemetry": None, "gps": None, "sync": None}

def main():
    """Fonction principale"""
    setup_interface()

    # Start the serial reader
    serial_reader = SerialReader()
    serial_reader.start()

    # Start the HTTP server for the map
    server = start_http_server(HTTP_PORT)

    dpg.create_viewport(
        title='Graphique avec Sources Multiples',
        width=1200,
        height=800
    )

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)

    # Boucle principale avec mise à jour du graphique
    while dpg.is_dearpygui_running():
        update_graph()  # Mise à jour périodique des graphiques
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
    serial_reader.stop()

if __name__ == "__main__":
    main()
