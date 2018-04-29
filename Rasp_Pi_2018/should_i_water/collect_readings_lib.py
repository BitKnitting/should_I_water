from RFM69_lib import RFM69
import datetime
from handle_logging_lib import HandleLogging
import struct
import sys

_MOISTURE_INFO_PACKET            =   1
_MOISTURE_INFO_PACKET_RECEIVED   =   2
_TIME_INFO_PACKET                =   3
_TEST_PACKET                     =   4
_NO_PACKET_TYPE                  =   100
_ERROR_IN_PACKET_RECEIVED        =   99
_TEST_VALUE                      =   0x1234

class Measurement:
    def __init__(self,callback):
        ''' start with an instance of the RFM69 radio and set the
        packet_received boolean to true.  This way, receive_begin
        will start in receive mode '''
        self.callback = callback
        self.radio =  RFM69()
        self.handle_logging = HandleLogging()

    def _receive_done(self,packet):
        '''
        This function is called back when a packet is received. We expect to
        either receive a request for time info or a moisture reading.
        If we don't understand the moisture reading, we send an error packet back.
        '''
        packet_list = list(packet)
        packet_type = _NO_PACKET_TYPE
        try:
            packet_type = packet_list[0]
        except IndexError as e:
            self.handle_logging.print_error(e)
        if packet_type == _TEST_PACKET:
            self.handle_logging.print_info("Received a _TEST_PACKET")
            packet_to_send = [_TEST_PACKET]
            self.radio.send(bytearray(packet_to_send))

        if packet_type == _TIME_INFO_PACKET:
            self.handle_logging.print_info("Received a _TIME_INFO_PACKET")
            # Send the current time and the watering hour.
            now = datetime.datetime.now()
            packet_to_send = [_TIME_INFO_PACKET, now.hour,now.minute,
                             now.second,self.watering_time]
            self.radio.send(bytearray(packet_to_send))
        elif packet_type == _MOISTURE_INFO_PACKET:
            self.handle_logging.print_info("Received a _MOISTURE_INFO_PACKET")
            # Remove the packet type byte
            del packet[0]
            # unpack the moisture readings
            try:
                nodeID,measurement,battery_level = struct.unpack('2hf',packet)
                battery_level = round(battery_level,2)
                self.callback(nodeID,measurement,battery_level)
                packet_to_send = [_MOISTURE_INFO_PACKET_RECEIVED]
            except struct.error as e:
                self.handle_logging.print_error(e)
                packet_to_send = [_ERROR_IN_PACKET_RECEIVED]

            self.radio.send(bytearray(packet_to_send))

    def begin(self,watering_time=4):
        # Watering time is on a 24 hour clock.
        self.watering_time = watering_time
        self.radio.receive_begin(callback=self._receive_done)
