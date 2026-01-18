import time
from machine import RTC
from hardware import gps_serial, my_gps, led

class GPSModule:
    def __init__(self):
        """Initialize GPS module"""
        self.has_gps_fix = False

    def init_gps_neo6m(self):
        """Configure NEO-6M GPS module"""
        time.sleep(1)
        gps_serial.write(
            b"$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n"
        )
        gps_serial.write(b"$PMTK220,1000*1F\r\n")
        print("NEO-6M GPS configured")

    def search_mode(self):
        """Search for GPS signal and set RTC"""
        print("Search Mode: Waiting for GPS time...")

        while not self.has_gps_fix:
            led.toggle()

            if gps_serial.any():
                data = gps_serial.read()
                for byte in data:
                    if my_gps.update(chr(byte)):
                        ds = my_gps.date
                        ts = my_gps.timestamp

                        if ds[2] >= 24:
                            self.has_gps_fix = True

                            rtc = RTC()
                            rtc.datetime((
                                2000 + ds[2],      # Year: ds[2] is last 2 digits, add 2000 (e.g., 23 → 2023)
                                ds[1],             # Month: ds[1] = month (1-12)
                                ds[0],             # Day: ds[0] = day of month
                                0,                 # Weekday: 0-6 for Monday-Sunday, 0=Monday (set to 0, will be calculated)
                                (ts[0] + 1) % 24,  # Hour: ts[0] = hour UTC, +1 adjusts timezone (e.g., UTC+1)
                                ts[1],             # Minute: ts[1] = minute
                                int(ts[2]),        # Second: ts[2] = second, convert to integer
                                0                  # Microsecond: set to 0 (not provided by GPS)
                            ))
                            return
            time.sleep(0.1)

    def get_sync_packet(self, counter):
        """Get sync packet with timestamp"""
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

    def get_gps_packet(self, counter, logger):
        """Get GPS position packet"""
        if gps_serial.any():
            data = gps_serial.read()
            for byte in data:
                if my_gps.update(chr(byte)):
                    if my_gps.date[2] >= 24:
                        self.has_gps_fix = True

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
