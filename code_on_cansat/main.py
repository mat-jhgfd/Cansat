import time
from hardware import led
from gps import GPSModule
from sensors import get_sensor_packet
from radio import RadioTransmitter
from logger_init import initialize_logger
from config import SYNC_INTERVAL

counter = 1

# Initialize modules
gps_module = GPSModule()
radio = RadioTransmitter()
logger = initialize_logger()

# GPS initialization
gps_module.init_gps_neo6m()
gps_module.search_mode()

print("Normal Mode started")

while True:
    led.toggle()
    
    # Transmit sync packet if no GPS fix or at sync interval
    if not gps_module.has_gps_fix or (counter % SYNC_INTERVAL == 0):
        radio.transmit(gps_module.get_sync_packet(counter))
        time.sleep(0.05)
    
    # Transmit sensor data
    radio.transmit(get_sensor_packet(counter, radio.last_rssi, logger))
    time.sleep(0.05)
    
    # Transmit GPS data if available
    gps_msg = gps_module.get_gps_packet(counter, logger)
    if gps_msg:
        radio.transmit(gps_msg)
        time.sleep(0.05)
    
    counter += 1
