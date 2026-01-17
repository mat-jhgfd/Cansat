import time
from hardware import led
import gps
from gps import init_gps_neo6m, search_mode, get_gps_packet, get_sync_packet
from sensors import get_sensor_packet
from radio import transmit, last_rssi
from logger_init import initialize_logger
from config import SYNC_INTERVAL

counter = 1

init_gps_neo6m()
search_mode()
logger = initialize_logger()

print("Normal Mode started")

while True:
    led.toggle()

    if not gps.has_gps_fix or (counter % SYNC_INTERVAL == 0):
        transmit(gps.get_sync_packet(counter))
        time.sleep(0.05)

    transmit(get_sensor_packet(counter, last_rssi, logger))
    time.sleep(0.05)

    gps_msg = get_gps_packet(counter, logger)
    if gps_msg:
        transmit(gps_msg)
        time.sleep(0.05)

    counter += 1

