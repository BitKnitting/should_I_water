# Copyright (c) 2018 Margaret Johnson for fun.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# 05/26/2018 - added figuring out what puck type an incoming message was from.
# moved reading the node id up to where the puck and packet type are read.
from RFM69_lib import RFM69
import datetime
from handle_logging_lib import HandleLogging
from reading_model import Node
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
        self.handle_logging.print_info("Initializing Measurement class.")
        self.node_id = None

    def _receive_done(self,packet):
        '''
        This function is called back when a packet is received. First we check
        if the packet is coming from a Moisture Puck.  If it isn't, we ignore
        the packet.  If it is a packet coming from a moisture puck, we expect to
        either receive a request for time info or a moisture reading.
        If we don't understand the moisture reading, we send an error packet back.
        '''
        packet_list = list(packet)
        packet_type = _NO_PACKET_TYPE
        try:
            packet_type = packet_list[0]
            self.node_id = packet_list[1]
            # look up the node_id in the node table.
            Node.initialize()
            try:
                node_info = Node.get(Node.nodeID == self.node_id)
                Node.close()
            except Node.DoesNotExist as e:
                self.handle_logging.print_error(e)
                Node.close()
                return
            if node_info.puck_type != "moisture":
                self.handle_logging.print_info("Received a packet, but was not from a moisture puck.")
                return
            # if the puck type is not a moisture puck, return (none?)
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
            packet_to_send = [_TIME_INFO_PACKET,  self.node_id,
                            now.hour, now.minute, now.second, self.watering_time]

            self.radio.send(bytearray(packet_to_send))
        elif packet_type == _MOISTURE_INFO_PACKET:
            self.handle_logging.print_info("Received a _MOISTURE_INFO_PACKET")
            # Remove the packet type and node id bytes
            # unpack the moisture readings
            try:
                # Take care to strip out the packet type and node id.
                measurement,battery_level = struct.unpack('=hf',packet[2:])
                battery_level = round(battery_level,2)
                self.callback(self.node_id,measurement,battery_level)
                packet_to_send = [_MOISTURE_INFO_PACKET_RECEIVED]
            except struct.error as e:
                self.handle_logging.print_error(e)
                packet_to_send = [_ERROR_IN_PACKET_RECEIVED]

            self.radio.send(bytearray(packet_to_send))

    def begin(self,watering_time=4):
        # Watering time is on a 24 hour clock.
        self.watering_time = watering_time
        self.radio.receive_begin(callback=self._receive_done)
