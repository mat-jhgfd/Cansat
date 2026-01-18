from hardware import rfm
from config import DEBUG

class RadioTransmitter:
    def __init__(self):
        self.last_rssi = 0.0

    def transmit(self, payload):
        try:
            ack = rfm.send_with_ack(payload.encode())
            if ack:
                self.last_rssi = rfm.rssi
                return True

            if DEBUG:
                print("TX:", payload)

        except Exception as e:
            print("RFM Error:", e)

        return False
