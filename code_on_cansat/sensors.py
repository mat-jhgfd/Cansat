from hardware import bmp
from config import BASELINE

def get_sensor_packet(counter, last_rssi, logger):
    try:
        if bmp is None:
            return "T,%d,%.1f,0,0,0,0" % (counter, last_rssi)

        t, p, h = bmp.raw_values
        if p <= 0:
            return "T,%d,%.1f,0,0,0,0" % (counter, last_rssi)

        alt = (BASELINE - p) * 8.3

        logger.add_info_line(
            f"Sensor data - T:{t}, P:{p}, H:{h}, Alt:{alt}"
        )

        return "T,%d,%.1f,%.1f,%.1f,%.0f,%.1f" % (
            counter, last_rssi, t, p, h, alt
        )

    except Exception as e:
        logger.add_error_line(f"Sensor Error: {e}")
        return "T,%d,%.1f,FAIL,FAIL,FAIL,FAIL" % (counter, last_rssi)
