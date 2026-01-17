from machine import SPI, Pin, UART, I2C
from rfm69 import RFM69
from bme280 import BME280, BMP280_I2CADDR
from micropyGPS import MicropyGPS
from config import FREQ, ENCRYPTION_KEY, NODE_ID, BASESTATION_ID

# LED
led = Pin(25, Pin.OUT)

# SPI / RFM69
spi = SPI(
    0,
    miso=Pin(4),
    mosi=Pin(7),
    sck=Pin(6),
    baudrate=50000,
    polarity=0,
    phase=0,
    firstbit=SPI.MSB
)

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

# I2C / BMP280
i2c = I2C(0, sda=Pin(8), scl=Pin(9))
try:
    bmp = BME280(i2c=i2c, address=BMP280_I2CADDR)
except Exception as e:
    print("BMP280 Init Failed:", e)
    bmp = None

# GPS
gps_serial = UART(0, baudrate=9600, tx=Pin(12), rx=Pin(13))
my_gps = MicropyGPS()
