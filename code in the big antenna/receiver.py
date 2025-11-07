import radio
from microbit import *
 
radio.on()
radio.config(channel = 10)
 
while True:
    received = radio.receive()
    if received:
        display.scroll(received)
