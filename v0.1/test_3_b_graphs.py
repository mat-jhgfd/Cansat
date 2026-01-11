"""
Sensors:
 Temperature (2)
 Altitude (2)
 Pression (1)
 rssi -> packet et ack
 Humidité (1)
 Accelerometre (1)
 Date (GPS) --> static
 Gyro (1)
 Compas (1)
- Position horizontale (1) -> axe x et y"""

graphs = [{"name": "Temperature (°C)", "abr": "temp", 
           "sensors":{"BME":(255, 10, 10), "ICM":(255, 150, 0)},
           "y_limits":(0,50)},

           {"name": "Altitude (m)", "abr": "alt", 
           "sensors":{"BME":(255, 10, 10), "ICM":(255, 150, 0)}},

           {"name": "Pression (hpa)", "abr": "pre", 
           "sensors":{"BME":(255, 10, 10)},
           "y_limits":(950,1050)},

           {"name": "RSSI (dbi)", "abr": "rss", 
           "sensors":{"ANT":(255, 255, 255)},
           "y_limits":(-120,0)},

           {"name": "ACK - Last 10", "abr": "ack", 
           "sensors":{"ANT":(255, 255, 255)},
           "y_limits":(0,10)},

           {"name": "Humidité (%)", "abr": "hum", 
           "sensors":{"BME":(255, 10, 10)},
           "y_limits":(0,100)},
           
           {"name": "Accéléromètre (-10~10)", "abr": "acc", 
           "sensors":{"ICM-x":(255, 10, 10), "ICM-y":(10, 255, 10), "ICM-z":(10, 10, 255)},
           "y_limits":(-10,10)},

           {"name": "Gyro (-1~1)", "abr": "gyr", 
           "sensors":{"ICM-x":(255, 10, 10), "ICM-y":(10, 255, 10), "ICM-z":(10, 10, 255)},
           "y_limits":(-1,1)},

           {"name": "Compas (°)", "abr": "mag",
            "sensors":{"ICM-x":(255, 10, 10), "ICM-y":(10, 255, 10), "ICM-z":(10, 10, 255)},
            "y_limits":(0,360)},

           {"name": "Position (m) --> target (TO CHANGE !!!)", "abr": "pos",
            "sensors":{"GPS-x":(255, 10, 10), "GPS-y":(10, 255, 10)}},
           ]

N_COLUMNS = 3

def setup_graphs(dpg):
    # Zone principale avec deux colonnes
    with dpg.child_window():
        with dpg.theme(tag="plot_theme"):
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 200, 255), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2, category=dpg.mvThemeCat_Plots)
        
        # Créer un groupe horizontal pour les deux colonnes
        with dpg.group(horizontal=True):
            # Créer les deux colonnes
            columns = [dpg.add_child_window(width=400) for _ in range(N_COLUMNS)]
            
            # Répartir les graphes dans les deux colonnes
            for i, entree in enumerate(graphs):
                # Choisir la colonne (0 ou 1)
                column = columns[i % N_COLUMNS]
                
                with dpg.group(parent=column):
                    name = entree["name"]
                    abr = entree["abr"]
                    sensors = entree["sensors"]
                    y_min, y_max = entree.get("y_limits", (None, None))
                    
                    for sensor_id, color in sensors.items():
                        with dpg.theme(tag=f"{abr}_source_theme_{sensor_id}"):
                            with dpg.theme_component(dpg.mvLineSeries):
                                dpg.add_theme_color(dpg.mvPlotCol_Line, color, category=dpg.mvThemeCat_Plots)
                                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2, category=dpg.mvThemeCat_Plots)
                    
                    with dpg.plot(
                        label=name,
                        height=200,
                        width=-1,
                        tag=f"{abr}_plot"
                    ):
                        # Axes
                        dpg.add_plot_axis(dpg.mvXAxis, label="", tag=f"{abr}_x_axis", auto_fit=True)
                        dpg.add_plot_axis(dpg.mvYAxis, label="", tag=f"{abr}_y_axis", auto_fit=True if y_min is None and y_max is None else False)
                        
                        if y_min is not None and y_max is not None:
                            dpg.set_axis_limits(f"{abr}_y_axis", y_min, y_max)
                            # Désactive le zoom et le déplacement sur X
                            dpg.configure_item(f"{abr}_y_axis", no_menus=True, lock_min=True, lock_max=True)
                        
                        # Série de données pour chaque source
                        for sensor_id in sensors.keys():
                            dpg.add_line_series(
                                [], [],
                                label=sensor_id,
                                parent=f"{abr}_y_axis",
                                tag=f"series_{abr}_{sensor_id}"
                            )
                            
                            # Applique les thèmes aux séries
                            dpg.bind_item_theme(f"series_{abr}_{sensor_id}", f"{abr}_source_theme_{sensor_id}")
                    
                    # Légende
                    dpg.add_plot_legend(parent=f"{abr}_plot", location=dpg.mvPlot_Location_NorthEast, tag=f"plot_legend_{abr}")