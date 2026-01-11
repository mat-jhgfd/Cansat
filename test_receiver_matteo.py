"""
CANSAT PICO Receiver node (With ACK + Encryption)
"""

from machine import SPI, Pin
from rfm69 import RFM69
import time

# --- Configuration ---
FREQ           = 433.1
ENCRYPTION_KEY = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
NODE_ID        = 100

# --- Hardware Setup ---
spi = SPI(0, miso=Pin(4), mosi=Pin(7), sck=Pin(6),
          polarity=0, phase=0, firstbit=SPI.MSB)
nss = Pin(5, Pin.OUT, value=True)
rst = Pin(3, Pin.OUT, value=False)

rfm = RFM69(spi=spi, nss=nss, reset=rst)
rfm.frequency_mhz = FREQ
rfm.encryption_key = ENCRYPTION_KEY
rfm.node = NODE_ID

print("Freq:", rfm.frequency_mhz)
print("NODE:", rfm.node)
print("Waiting for packets (with ACK + encryption)...")

while True:
    packet = rfm.receive(with_ack=True)
    if packet is not None:
        packet_text = str(packet, "ascii")
        rssi = rfm.rssi
        print("Received:", packet_text)
        print("RSSI: %3.1f dBm" % rssi)
        print("ACK sent back automatically.")

        # Parse the packet based on the type
        if packet_text.startswith("T,"):
            # Telemetry packet: T, counter, rssi, temperature, pressure, humidity, altitude
            parts = packet_text.split(",")
            counter = parts[1]
            rssi = parts[2]
            temperature = parts[3]
            pressure = parts[4]
            humidity = parts[5]
            altitude = parts[6]
            print(f"Telemetry - Counter: {counter}, RSSI: {rssi}, Temp: {temperature}, Pressure: {pressure}, Humidity: {humidity}, Altitude: {altitude}")

        elif packet_text.startswith("G,"):
            # GPS packet: G, counter, latitude, longitude, altitude, satellites
            parts = packet_text.split(",")
            counter = parts[1]
            latitude = parts[2]
            longitude = parts[3]
            altitude = parts[4]
            satellites = parts[5]
            print(f"GPS - Counter: {counter}, Lat: {latitude}, Lon: {longitude}, Alt: {altitude}, Sats: {satellites}")

        elif packet_text.startswith("S,"):
            # Sync packet: S, counter, time, date
            parts = packet_text.split(",")
            counter = parts[1]
            time_str = parts[2]  # Changed from 'time' to 'time_str'
            date_str = parts[3]  # Changed from 'date' to 'date_str'
            print(f"Sync - Counter: {counter}, Time: {time_str}, Date: {date_str}")

        print("-" * 40)
    time.sleep(0.05)

