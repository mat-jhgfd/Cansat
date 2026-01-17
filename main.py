"""
CANSAT PICO Emitter node (With ACK + Encryption)

Modes:
1. Search Mode: Initialize GPS and wait for valid time.
2. Normal Mode: Start all components, log data, and handle errors.
"""

from machine import SPI, Pin, UART, I2C
from rfm69 import RFM69
import time
from test_tobias import Logger
from micropyGPS import MicropyGPS
from bme280 import BME280, BMP280_I2CADDR

# --- Configuration ---
FREQ           = 433.1
ENCRYPTION_KEY = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
NODE_ID        = 120
BASESTATION_ID = 100
baseline       = 1019.0
SYNC_INTERVAL  = 50

# --- Hardware Setup ---
led = Pin(25, Pin.OUT)
spi = SPI(0, miso=Pin(4), mosi=Pin(7), sck=Pin(6),
          baudrate=50000, polarity=0, phase=0, firstbit=SPI.MSB)
nss = Pin(5, Pin.OUT, value=True)
rst = Pin(3, Pin.OUT, value=False)

rfm = RFM69(spi=spi, nss=nss, reset=rst)
rfm.frequency_mhz = FREQ
rfm.tx_power = 20
rfm.encryption_key = ENCRYPTION_KEY
rfm.node = NODE_ID
rfm.destination = BASESTATION_ID
rfm.ack_retries = 2
rfm.ack_wait = 0.1

i2c = I2C(0, sda=Pin(8), scl=Pin(9))

try:
    bmp = BME280(i2c=i2c, address=BMP280_I2CADDR)
except Exception as e:
    print(f"BMP280 Init Failed: {e}")
    bmp = None

logger = None
my_gps = MicropyGPS()
gps_serial = UART(0, baudrate=9600, tx=Pin(12), rx=Pin(13))

# --- State Variables ---
counter = 1
last_rssi = 0.0
has_gps_fix = False
search_mode_active = True

def init_gps_neo6m():
    time.sleep(1)  # Let GPS boot

    # Enable RMC + GGA only (clean + low bandwidth)
    gps_serial.write(
        b"$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n"
    )

    # Set update rate to 1Hz (stable for MicropyGPS)
    gps_serial.write(
        b"$PMTK220,1000*1F\r\n"
    )

    print("NEO-6M GPS configured")

def search_mode():
    """Initialize GPS and wait for valid time. LED blinks fast during search mode."""
    from machine import RTC
    global has_gps_fix, search_mode_active, sync_ms
    print("Search Mode: Initializing GPS and waiting for valid time...")
    while not has_gps_fix:
        try:
            led.toggle()
            if gps_serial.any():
                data = gps_serial.read()
                if data:
                    for byte in data:
                        if my_gps.update(chr(byte)):
                           # ds is [Day, Month, Year]
                            ds = my_gps.date 
                            ts = my_gps.timestamp # [Hour, Minute, Second]

                            if ds[2] >= 24: # Check if year is 2024 or later
                                has_gps_fix = True
                                
                                # 1. Correct the Year
                                year = 2000 + ds[2]
                                # 2. Map Month and Day correctly from the array
                                month = ds[1]
                                day = ds[0]
                                
                                # 3. Handle Timezone (UTC+1)
                                hour = (ts[0] + 1) % 24
                                minute = ts[1]
                                second = ts[2]

                                # 4. Set the RTC with the strictly ordered tuple
                                rtc = RTC()
                                # Order: (year, month, day, weekday, hours, minutes, seconds, subseconds)
                                rtc.datetime((year, month, day, 0, hour, minute, int(second), 0))
                                sync_ms = time.ticks_ms() # Capture the exact hardware tick at sync

                                search_mode_active = False
                                return
        except Exception as e:
            print(f"Search Mode: GPS Error: {e}")
        time.sleep(0.1)

def get_sensor_packet():
    try:
        if bmp is None:
            logger.add_error_line("BMP280 not initialized.")
            return "T,%d,0,ERR,ERR,ERR,ERR" % counter
        t, p, h = bmp.raw_values
        if p is None or p == 0:
            logger.add_error_line("Invalid pressure value.")
            return "T,%d,%.1f,0,0,0,0" % (counter, last_rssi)
        alt = (baseline - p) * 8.3
        log_message = f"Sensor data - T: {t}, P: {p}, H: {h}, Alt: {alt}"
        logger.add_info_line(log_message)
        return "T,%d,%.1f,%.1f,%.1f,%.0f,%.1f" % (counter, last_rssi, t, p, h, alt)
    except Exception as e:
        logger.add_error_line(f"Sensor Read Error: {e}")
        return "T,%d,%.1f,FAIL,FAIL,FAIL,FAIL" % (counter, last_rssi)

def get_gps_packet():
    global has_gps_fix
    try:
        if gps_serial.any():
            data = gps_serial.read()
            if data:
                for byte in data:
                    if my_gps.update(chr(byte)):

                        # Check fix once
                        if my_gps.date[2] >= 24:
                            has_gps_fix = True

                        # Read GPS values ONCE
                        lat = my_gps.latitude_string()
                        lon = my_gps.longitude_string()
                        alt = my_gps.altitude
                        sats = my_gps.satellites_in_use

                        # Log using cached values
                        logger.add_info_line(
                            f"GPS data - Lat: {lat}, Lon: {lon}, Alt: {alt}, Sats: {sats}"
                        )

                        # Use same cached values for packet
                        return "G,%d,%s,%s,%4.1f,%d" % (
                            counter,
                            lat,
                            lon,
                            alt,
                            sats
                        )

    except Exception as e:
        logger.add_error_line(f"GPS Error: {e}")

    return None

def get_sync_packet():
    try:
        ts = my_gps.timestamp
        ds = my_gps.date
        time_str = "%02d:%02d:%02d" % (ts[0], ts[1], ts[2])
        date_str = "%02d/%02d/%02d" % (ds[0], ds[1], ds[2])
        log_message = f"Sync packet - Time: {time_str}, Date: {date_str}"
        logger.add_info_line(log_message)
        return "S,%d,%s,%s" % (counter, time_str, date_str)
    except:
        return "S,%d,ERR,ERR" % counter

def transmit(payload):
    global last_rssi
    try:
        print("TX:", payload)
        ack = rfm.send_with_ack(bytes(payload, "utf-8"))
        if ack:
            last_rssi = rfm.rssi
            return True
    except Exception as e:
        print(f"RFM TX Error: {e}")
    return False

def initialize_logger():
    """Initialize logger with current date and time from the now-set RTC."""
    global logger
    
    # Now that RTC is set by search_mode, Logger() will 
    # pick up the correct system time for file naming/internal headers
    logger = Logger() 
    
    # Get current time from RTC for the first log entry
    now = time.localtime()
    date_str = "%04d-%02d-%02d" % (now[0], now[1], now[2])
    time_str = "%02d:%02d:%02d" % (now[3], now[4], now[5])
    
    logger.add_info_line(f"Logger started after GPS Sync at {date_str} {time_str}")
    print(f"Logger initialized. Log file: {logger.log_file_path}")

# --- Main Loop ---
init_gps_neo6m()
print("CANSAT Node Active. Starting in Search Mode.")
search_mode()
initialize_logger()
print("Switching to Normal Mode. All components starting...")

while True:
    try:
        led.toggle()

        # 1. Handle Time Sync
        if not has_gps_fix or (counter % SYNC_INTERVAL == 0):
            transmit(get_sync_packet())
            time.sleep(0.05)

        # 2. Telemetry
        transmit(get_sensor_packet())
        time.sleep(0.05)

        # 3. GPS
        g_msg = get_gps_packet()
        if g_msg:
            transmit(g_msg)
            time.sleep(0.05)

    except Exception as e:
        logger.add_error_line(f"Main Loop Warning: {e}")

    counter += 1
    time.sleep(0.2)

