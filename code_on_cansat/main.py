import time
from hardware import led
from gps import GPSModule
from sensors import get_sensor_packet
from radio import RadioTransmitter
from logger_init import initialize_logger
from config import SYNC_INTERVAL, DEBUG

counter = 1
last_sensor_time = 0

# Initialize modules
gps_module = GPSModule()
radio = RadioTransmitter()
logger = initialize_logger()

# GPS initialization
gps_module.init_gps_neo6m()

# If DEBUG is True, skip GPS search mode and set a default time
if not DEBUG:
    gps_module.search_mode()
    print("Normal Mode started")
else:
    # In DEBUG mode, don't wait for GPS fix, just use system tick
    from machine import RTC
    import utime
    # Set RTC to a default time for debugging
    rtc = RTC()
    # Use current system tick time for logging
    tick_time = utime.time()
    # Convert to datetime format: (year, month, day, weekday, hour, minute, second, microsecond)
    time_tuple = time.localtime(tick_time)
    rtc.datetime((
        time_tuple[0],  # year
        time_tuple[1],  # month
        time_tuple[2],  # day
        time_tuple[6],  # weekday
        time_tuple[3],  # hour
        time_tuple[4],  # minute
        time_tuple[5],  # second
        0               # microsecond
    ))
    # Mark as having GPS fix for normal operation flow
    gps_module.has_gps_fix = True
    print("DEBUG mode: Skipped GPS search, using system time")


# Initialize last_sensor_time
last_sensor_time = time.ticks_ms()

while True:
    led.toggle()
    
    current_time = time.ticks_ms()
    
    # Transmit sensor data every 1 second
    if time.ticks_diff(current_time, last_sensor_time) >= 1000:
        radio.transmit(get_sensor_packet(counter, radio.last_rssi, logger))
        last_sensor_time = current_time
        counter += 1
    
    # Transmit sync packet if no GPS fix or at sync interval
    # This runs independently of the 1-second sensor interval
    if not gps_module.has_gps_fix or (counter % SYNC_INTERVAL == 0):
        radio.transmit(gps_module.get_sync_packet(counter))
        time.sleep(0.05)
    
    # Transmit GPS data if available
    # This runs independently of the 1-second sensor interval
    gps_msg = gps_module.get_gps_packet(counter, logger)
    if gps_msg:
        radio.transmit(gps_msg)
        time.sleep(0.05)
    
    time.sleep(0.01)
