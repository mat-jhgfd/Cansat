# Read the TMP69 analog temperature sensor 
#    sensor wired to ADC0 (GP26)
#
from machine import ADC, Pin

# Deactivate PowerSafe (lower ripple)
Pin( 23, Pin.OUT, value=True )

adc = ADC(Pin(26))
while True:
    value = adc.read_u16()
    mv = 3300.0 * value / 65535
    temp = (mv-500)/10
    print( 'Temp: %5.2f °C, Voltage: %4i mV' % (temp,mv) )
    