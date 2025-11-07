from machine import Pin, ADC
import time

led = Pin(25, Pin.OUT)
led.value(0)
adc = ADC(Pin(26)) #TMP36

while temp <29:
#Get Data from Temp sensor
    value = adc.read_u16() #read pin value
    mv = 3300.0 * value/ 65535 #scale data between 0V and 3.3V
    temp = (mv - 500) / 10 #convert data following datasheet
    print (temp) #display temperature 
    time.sleep(0.4) # wait beofre next reading
    
if temp > 29:
    led.value(1)
    print(overheat)