# copy/paste this code into a Python session opened on a Feather...
import board
import busio
import digitalio
import adafruit_rfm69
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM69_CS)
RESET = digitalio.DigitalInOut(board.RFM69_RST)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, RADIO_FREQ_MHZ)
print('Waiting for packets...')
while True:
    packet = rfm69.receive()
    if packet is None:
        print('Received nothing! Listening again...')
    else:
        packet_text = str(packet, 'ascii')
        print('Received (ASCII): {0}'.format(packet_text))
