from hardware import rfm
from config import DEBUG

last_rssi = 0.0

def transmit(payload):
    global last_rssi
    try:
        ack = rfm.send_with_ack(payload.encode())
        if ack:
            last_rssi = rfm.rssi
            return True
        if DEBUG:
            print("TX:", payload)

    except Exception as e:
        print("RFM Error:", e)
    return False
