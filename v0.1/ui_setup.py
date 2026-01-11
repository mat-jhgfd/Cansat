import dearpygui.dearpygui as dpg
import test_3_base_ui
import test_3_left_menu
import test_3_b_graphs

def setup_interface():
    """Configure l'interface graphique"""
    dpg.create_context()

    # Crée la fenêtre principale
    with dpg.window(tag="Primary Window", label="Graphique avec Sources Multiples"):
        # Menu d'en-tête
        test_3_base_ui.setup_base_ui(dpg)

        # Panneau de contrôle à gauche
        with dpg.group(horizontal=True):
            # Zone de menu à gauche
            test_3_left_menu.setup_left_menu(dpg)

            test_3_b_graphs.setup_graphs(dpg)

        # Add a button to open the map in the browser
        dpg.add_button(label="Open map in browser", tag="open_map_button",
                       callback=lambda: webbrowser.open(f"http://127.0.0.1:{HTTP_PORT}/map.html"))
