#
# The WateringPuck class knows how to receive water messages
# from the app on the Rasp Pi and then turn on "the right valve"
# watering for the amount of time given the packet received.

import board
import busio
import digitalio
import time
import adafruit_rfm69

_START_WATERING_PACKET = 5
_STOP_WATERING_PACKET = 6
_VALVE = board.D12


class WateringPuck:
    def __init__(self, node_id, pin):
        # initialize the RFM69 radio on the Feather
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        cs = digitalio.DigitalInOut(board.RFM69_CS)
        reset = digitalio.DigitalInOut(board.RFM69_RST)
        self.rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0)
        self.packet = None
        self.node_id = node_id
        # Initialize the pin used to turn valve on/off.
        self.valve = digitalio.DigitalInOut(pin)
        self.valve.direction = digitalio.Direction.OUTPUT
        self.valve.value = False
        # start and stop watering markers are used with time.monotonic() to
        # figure out whether to turn of watering.
        self.start_watering_marker = 0
        self.stop_watering_marker = 0
        self.watering = False
        self.led = digitalio.DigitalInOut(board.D13)
        self.led.direction = digitalio.Direction.OUTPUT

    def water_packet_check(self):
        '''
        water_packet_check checks with the RFM69 to see if a start or stop watering
        packet has been received.

        '''
        # If watering and amount of watering minutes has been met, turn valve off.
        if self._should_stop_watering():
            self._stop_watering()
        # If currently watering, check if it is time to stop watering
        self.packet = self.rfm69.receive()
        # The first two bytes of our traffic:
        # byte 0: Type of packet
        # byte 1: Node ID
        # rest of bytes: specific to the type of packet.  In the
        # case of the watering info structure:
        #  uint8_t packet_type;
        #  uint8_t node_id;
        #  uint8_t valve_id;
        #  uint8_t watering_minutes;
        if self.packet is not None:
            if self.packet[1] != self.node_id:
                return False
            # This packet was for us.  Was it a "time to water" packet?
            if self.packet[0] != _START_WATERING_PACKET and self.packet[0] != _STOP_WATERING_PACKET:
                return False
            if self.packet[0] == _STOP_WATERING_PACKET:
                self._stop_watering()
                return True
            else:  # start watering packet
                self.watering_minutes = self.packet[3]
                self._start_watering(self.packet[3])
                return True
        return False

    def _should_stop_watering(self):
        if self.watering:
            now_time = time.monotonic()
            if now_time > self.stop_watering_marker:
                return True
        return False

    def _start_watering(self, watering_minutes):
        '''
        We will turn the valve on for the amount of minutes in
        watering_minutes
        '''
        self.watering = True
        self.valve.value = True
        self.start_watering_marker = time.monotonic()
        self.stop_watering_marker = self.start_watering_marker + watering_minutes * 60
        self._blink(3)

    def _stop_watering(self):
        self.watering = False
        self.valve.value = False
        self.start_watering_marker = 0
        self.stop_watering_marker = 0
        self._blink(5)

    def _blink(self, numBlinks):
        for _ in range(numBlinks):
            self.led.value = True
            time.sleep(.3)
            self.led.value = False
            time.sleep(.3)
