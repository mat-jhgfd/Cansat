""" CANSAT PICO Emitter node (CanSat)

Emit message to the base station and wait for ACK (500ms max) over
RFM69HCW SPI module - EMITTER node
Must be tested togheter with test_receiver

See Tutorial : https://wiki.mchobby.be/index.php?title=ENG-CANSAT-PICO-RFM69HCW-TEST
See GitHub : https://github.com/mchobby/cansat-belgium-micropython/tree/main/test-rfm69

RFM69HCW breakout : https://shop.mchobby.be/product.php?id_product=1390
RFM69HCW breakout : https://www.adafruit.com/product/3071
"""

from machine import SPI, Pin
from rfm69 import RFM69
import time

led = Pin( 25, Pin.OUT )

FREQ           = 433.1
ENCRYPTION_KEY = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
NODE_ID        = 120 # ID of this node
BASESTATION_ID = 100 # ID of the node (base station) to be contacted

spi = SPI(0, miso=Pin(4), mosi=Pin(7), sck=Pin(6), baudrate=50000, polarity=0, phase=0, firstbit=SPI.MSB)
nss = Pin( 5, Pin.OUT, value=True )
rst = Pin( 3, Pin.OUT, value=False )

rfm = RFM69( spi=spi, nss=nss, reset=rst )
rfm.frequency_mhz = FREQ
rfm.tx_power = 20 # 20 dBm (maximum)

# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm.encryption_key = ( ENCRYPTION_KEY )
rfm.node    = NODE_ID # This instance is the node 120

print( 'Freq            :', rfm.frequency_mhz )
print( 'NODE            :', rfm.node )
print( 'BaseStation NODE:', BASESTATION_ID )

# Send a packet and waits for its ACK.
# Note you can only send a packet up to 60 bytes in length.
counter = 1
last_rssi       = None # Capture the RSSI when receing ack
rfm.ack_retries = 3 # 3 attempt to receive ACK
rfm.ack_wait    = 0.5 # 500ms, time to wait for ACK 
rfm.destination = BASESTATION_ID # Send to specific node 100
while True:
	led.toggle()
	print("Send message %i!" % counter)
	ack = rfm.send_with_ack(bytes("M %i lr %3.1f" % (counter,0 if last_rssi==None else last_rssi) , "utf-8") )
	print("   +->", "ACK received" if ack else "ACK missing" )
	# Get the RSSI value when received the ACK --> to send within the next MSG
	if ack:
		last_rssi = rfm.rssi
	counter += 1
	time.sleep(1)
