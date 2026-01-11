def setup_left_menu(dpg):
    with dpg.child_window(width=200):
                dpg.add_text("Contrôles des Sources")
                dpg.add_separator()
                
                # Checkboxes pour activer/désactiver les sources
                dpg.add_checkbox(
                    label="Source 1",
                    default_value=True,
                    user_data="source_1",
                    tag="checkbox_source_1"
                )
                dpg.add_checkbox(
                    label="Source 2", 
                    default_value=True,
                    user_data="source_2",
                    tag="checkbox_source_2"
                )
                dpg.add_checkbox(
                    label="Source 3",
                    default_value=True,
                    user_data="source_3",
                    tag="checkbox_source_3"
                )
                
                dpg.add_spacer()
                dpg.add_separator()
                dpg.add_spacer()
                
                # Affichage des valeurs courantes
                dpg.add_text("Valeurs courantes:")
                dpg.add_text("", tag="current_values")
                
                dpg.add_spacer()
                dpg.add_button(label="Mettre à jour maintenant")
                dpg.add_button(label="Effacer tout")
                
                dpg.add_spacer()
                dpg.add_text("", tag="interval_value")
                dpg.set_value("interval_value", f"Intervalle: {00:.2f}s")
                
                dpg.add_spacer()
                dpg.add_text("", tag="status_text")