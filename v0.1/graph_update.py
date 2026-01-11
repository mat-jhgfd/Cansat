import dearpygui.dearpygui as dpg
import time
from shared_state import telemetry_lock, telemetry_latest, history

# Données historiques pour les graphiques
historical_data = {
    "source_1": [],
    "source_2": [],
}

# Configuration du graphique
MAX_POINTS = 100  # Nombre maximum de points affichés
update_interval = 0.1  # Intervalle de mise à jour en secondes
last_update_time = 0

def update_graph():
    """Met à jour les graphiques avec de nouvelles données"""
    global last_update_time

    current_time = time.time()

    # Vérifie si suffisamment de temps s'est écoulé depuis la dernière mise à jour
    if current_time - last_update_time >= update_interval:
        # Met à jour les séries du graphique avec les données partagées
        with telemetry_lock:
            t = telemetry_latest.get("telemetry")
            if t:
                # Mise à jour des données historiques avec les valeurs de télémétrie
                for key in ["temp", "pre", "hum", "alt", "rss"]:
                    if key in history:
                        historical_data["source_1"] = history[key][-MAX_POINTS:] if key == "temp" else historical_data["source_1"]
                        historical_data["source_2"] = history[key][-MAX_POINTS:] if key == "alt" else historical_data["source_2"]

        # Met à jour les séries du graphique
        for source_name, data in historical_data.items():
            dt = ["temp", "alt", "pre"]  # Liste des types de données à mettre à jour
            for tt in dt:
                series_id = f"series_{tt}_BME" if source_name == "source_1" else f"series_{tt}_ICM"
                if dpg.does_item_exist(series_id):
                    # Crée les données x (indices) et y (valeurs)
                    x_data = list(range(len(data)))
                    dpg.set_value(series_id, [x_data, data])

        # Met à jour l'affichage des valeurs courantes
        values_text = ""
        with telemetry_lock:
            t = telemetry_latest.get("telemetry")
            g = telemetry_latest.get("gps")
            if t:
                values_text += f"Temp: {t.get('temp', '?')} °C\n"
                values_text += f"Pressure: {t.get('pressure', '?')} hPa\n"
                values_text += f"Humidity: {t.get('humidity', '?')} %\n"
                values_text += f"Altitude: {t.get('altitude', '?')} m\n"
                values_text += f"RSSI: {t.get('rssi', '?')} dBm\n"
            if g:
                values_text += f"GPS: {g.get('lat', '?')}, {g.get('lon', '?')}\n"
        dpg.set_value("current_values", values_text)

        last_update_time = current_time

def toggle_source(sender, app_data, user_data):
    """Active/désactive l'affichage d'une source"""
    source_name = user_data
    series_id = f"series_{source_name}"

    if dpg.does_item_exist(series_id):
        visible = dpg.is_item_visible(series_id)
        dpg.configure_item(series_id, show=not visible)

        # Met à jour l'état de la checkbox
        dpg.set_value(f"checkbox_{source_name}", not visible)

def change_update_interval(sender, app_data):
    """Change l'intervalle de mise à jour"""
    global update_interval
    update_interval = app_data
    dpg.set_value("interval_value", f"Intervalle: {update_interval:.2f}s")

def clear_graphs():
    """Efface toutes les données des graphiques"""
    for source_name in historical_data.keys():
        historical_data[source_name].clear()
        series_id = f"series_{source_name}"
        if dpg.does_item_exist(series_id):
            dpg.set_value(series_id, [[], []])

def save_data():
    """Fonction de sauvegarde des données (exemple)"""
    print("Données sauvegardées:", historical_data)
    dpg.set_value("status_text", "Données sauvegardées!")

def manual_update():
    """Mise à jour manuelle des graphiques"""
    update_graph()
    dpg.set_value("status_text", "Mise à jour manuelle effectuée!")
