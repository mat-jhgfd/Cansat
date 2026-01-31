import time
from hardware import led
from gps import GPSModule
from sensors import get_sensor_packet
from radio import RadioTransmitter
from logger_init import initialize_logger
from config import SYNC_INTERVAL, SENSOR_INTERVAL_SECONDS, DEBUG

counter = 1

# Initialize modules
gps_module = GPSModule()
radio = RadioTransmitter()
logger = initialize_logger()
last_sensor_time = time.time()

# GPS initialization
gps_module.init_gps_neo6m()
if not DEBUG:
    gps_module.search_mode()
    print("Normal Mode started")
else :
    print("Debug mode activated, gps not prioritised")
    gps_module.has_gps_fix = True

while True:
    led.toggle()
    
    # Transmit sync packet if no GPS fix or at sync interval
    if not gps_module.has_gps_fix or (counter % SYNC_INTERVAL == 0):
        radio.transmit(gps_module.get_sync_packet(counter))
        time.sleep(0.05)
    
    # Transmit sensor data ONLY every 1 second
    current_time = time.time()
    if current_time - last_sensor_time >= SENSOR_INTERVAL_SECONDS:
        radio.transmit(get_sensor_packet(counter, radio.last_rssi, logger))
        time.sleep(0.05)
        last_sensor_time = current_time
    
    # Transmit GPS data if available
    gps_msg = gps_module.get_gps_packet(counter, logger)
    if gps_msg:
        radio.transmit(gps_msg)
        time.sleep(0.05)
    
    counter += 1
