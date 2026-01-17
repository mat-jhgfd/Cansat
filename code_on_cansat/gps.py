import time
from machine import RTC
from hardware import gps_serial, my_gps, led

has_gps_fix = False

def init_gps_neo6m():
    time.sleep(1)
    gps_serial.write(
        b"$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n"
    )
    gps_serial.write(b"$PMTK220,1000*1F\r\n")
    print("NEO-6M GPS configured")

def search_mode():
    global has_gps_fix
    print("Search Mode: Waiting for GPS time...")

    while not has_gps_fix:
        led.toggle()

        if gps_serial.any():
            data = gps_serial.read()
            for byte in data:
                if my_gps.update(chr(byte)):
                    ds = my_gps.date
                    ts = my_gps.timestamp

                    if ds[2] >= 24:
                        has_gps_fix = True

                        rtc = RTC()
                        rtc.datetime((
                            2000 + ds[2],
                            ds[1],
                            ds[0],
                            0,
                            (ts[0] + 1) % 24,
                            ts[1],
                            int(ts[2]),
                            0
                        ))
                        return
        time.sleep(0.1)

def get_sync_packet(counter):
    try:
        ts = my_gps.timestamp
        ds = my_gps.date
        return "S,%d,%02d:%02d:%02d,%02d/%02d/%02d" % (
            counter,
            ts[0], ts[1], ts[2],
            ds[0], ds[1], ds[2]
        )
    except:
        return "S,%d,ERR,ERR" % counter

def get_gps_packet(counter, logger):
    global has_gps_fix

    if gps_serial.any():
        data = gps_serial.read()
        for byte in data:
            if my_gps.update(chr(byte)):
                if my_gps.date[2] >= 24:
                    has_gps_fix = True

                lat  = my_gps.latitude_string()
                lon  = my_gps.longitude_string()
                alt  = my_gps.altitude
                sats = my_gps.satellites_in_use

                logger.add_info_line(
                    f"GPS data - Lat:{lat}, Lon:{lon}, Alt:{alt}, Sats:{sats}"
                )

                return "G,%d,%s,%s,%4.1f,%d" % (
                    counter, lat, lon, alt, sats
                )
    return None
