# copy/paste this code into a Python session opened on a Feather...
import board
import busio
import digitalio

import adafruit_rfm69
import time

RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM69_CS)
RESET = digitalio.DigitalInOut(board.RFM69_RST)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, RADIO_FREQ_MHZ)
while True:
    rfm69.send('Hi!')
    time.sleep(1)
