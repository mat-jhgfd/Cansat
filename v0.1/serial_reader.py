import serial
import threading
import time
import re
from shared_state import telemetry_lock, telemetry_latest, history, gps_history

class SerialReader(threading.Thread):
    def __init__(self, port="/dev/ttyACM0", baud=115200):
        super().__init__(daemon=True)
        self.port = port
        self.baud = baud
        self.ser = None
        self.running = True
        self._open_serial()

    def _open_serial(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            print(f"Opened serial {self.port} @ {self.baud}")
        except Exception as e:
            print("Serial open error:", e)
            self.ser = None

    def run(self):
        while self.running:
            if not self.ser:
                time.sleep(1.0)
                continue
            try:
                raw = self.ser.readline().decode(errors="ignore").strip()
                if not raw:
                    continue
                if raw.startswith("Received:"):
                    line = raw.replace("Received:", "").strip()
                else:
                    line = raw
                print("RAW:", raw)

                if line.startswith("T,"):
                    parsed = self._parse_T(line)
                    if parsed:
                        with telemetry_lock:
                            telemetry_latest["telemetry"] = parsed
                            history["temp"].append(parsed["temp"])
                            history["pre"].append(parsed["pressure"])
                            history["hum"].append(parsed["humidity"])
                            history["alt"].append(parsed["altitude"])
                            history["rss"].append(parsed["rssi"])
                            for k in history:
                                if len(history[k]) > MAX_POINTS:
                                    history[k].pop(0)
                        print("PARSED T:", parsed)
                elif line.startswith("G,"):
                    parsed = self._parse_G(line)
                    if parsed:
                        latf = gps_to_float(parsed["lat_raw"])
                        lonf = gps_to_float(parsed["lon_raw"])
                        with telemetry_lock:
                            telemetry_latest["gps"] = {
                                "counter": parsed["counter"],
                                "lat_raw": parsed["lat_raw"],
                                "lon_raw": parsed["lon_raw"],
                                "lat": latf,
                                "lon": lonf,
                                "altitude": parsed["altitude"],
                                "sats": parsed["sats"],
                            }
                            if latf is not None and lonf is not None:
                                gps_history["lat"].append(latf)
                                gps_history["lon"].append(lonf)
                                gps_history["alt"].append(parsed["altitude"])
                                gps_history["sats"].append(parsed["sats"])
                                for kk in gps_history:
                                    if len(gps_history[kk]) > MAX_POINTS:
                                        gps_history[kk].pop(0)
                        print("PARSED G:", parsed)
                elif line.startswith("S,"):
                    parsed = self._parse_S(line)
                    if parsed:
                        with telemetry_lock:
                            telemetry_latest["sync"] = parsed
                        print("PARSED S:", parsed)
                elif "ACK RSSI:" in line:
                    parsed = self._parse_ACK(line)
                    if parsed:
                        print("PARSED ACK RSSI:", parsed)
            except Exception as e:
                print("Serial read error:", e)
                time.sleep(0.05)

    def _parse_T(self, line):
        try:
            parts = line.split(",")
            if len(parts) != 7:
                return None
            return {
                "counter": int(parts[1]),
                "rssi": float(parts[2]),
                "temp": float(parts[3]),
                "pressure": float(parts[4]),
                "humidity": float(parts[5]),
                "altitude": float(parts[6]),
            }
        except Exception as e:
            print("Telemetry parse error:", e, line)
            return None

    def _parse_G(self, line):
        try:
            parts = line.split(",")
            if len(parts) != 6:
                return None
            return {
                "counter": int(parts[1]),
                "lat_raw": parts[2].strip(),
                "lon_raw": parts[3].strip(),
                "altitude": float(parts[4]),
                "sats": int(parts[5]),
            }
        except Exception as e:
            print("GPS parse error:", e, line)
            return None

    def _parse_S(self, line):
        try:
            parts = line.split(",")
            if len(parts) != 4:
                return None
            return {"counter": int(parts[1]), "time": parts[2], "date": parts[3]}
        except Exception as e:
            print("Sync parse error:", e, line)
            return None

    def _parse_ACK(self, line):
        try:
            if "ACK RSSI:" in line:
                parts = line.split(":")
                rssi = float(parts[-1].strip().split()[0])
                with telemetry_lock:
                    history["ack_rss"].append(rssi)
                    if len(history["ack_rss"]) > MAX_POINTS:
                        history["ack_rss"].pop(0)
                print("PARSED ACK RSSI:", rssi)
                return rssi
        except Exception as e:
            print("ACK RSSI parse error:", e, line)
            return None

    def stop(self):
        self.running = False
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except:
            pass

def gps_to_float(coord: str):
    if not coord:
        return None
    s = coord.strip()
    m = re.match(r"^\s*(\d+)[°\s]+([\d\.]+)'\s*([NSEWnsew])\s*$", s)
    if m:
        deg = float(m.group(1))
        minutes = float(m.group(2))
        dirc = m.group(3).upper()
        val = deg + minutes / 60.0
        if dirc in ("S", "W"):
            val = -val
        return val
    m2 = re.match(r"^\s*([\d\.]+)\s*([NSEWnsew])\s*$", s)
    if m2:
        val = float(m2.group(1))
        dirc = m2.group(2).upper()
        if dirc in ("S", "W"):
            val = -val
        return val
    try:
        return float(s)
    except Exception:
        return None
