def setup_base_ui(dpg):
    # Menu d'en-tête
        with dpg.menu_bar():
            with dpg.menu(label="Fichier"):
                dpg.add_menu_item(label="Sauvegarder", callback=None)
                dpg.add_menu_item(label="Effacer les graphiques", callback=None)
                dpg.add_separator()
                dpg.add_menu_item(label="Quitter", callback=lambda: dpg.stop_dearpygui())
            
            with dpg.menu(label="Vue"):
                dpg.add_menu_item(label="Plein écran", callback=lambda: dpg.toggle_viewport_fullscreen())
                dpg.add_checkbox(label="Afficher la légende", default_value=True, tag="show_legend", 
                               callback=lambda s, a: dpg.configure_item("plot_legend", show=a))
            
            with dpg.menu(label="Paramètres"):
                dpg.add_slider_float(
                    label="Intervalle de mise à jour",
                    min_value=0.1,
                    max_value=2.0,
                    default_value=0,
                    callback=None,
                    tag="interval_slider"
                )