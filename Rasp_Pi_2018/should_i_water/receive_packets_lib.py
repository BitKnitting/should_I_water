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
#
# 05/29/2018 - Refactored so handling RFM69 packet logic can be shared.
from RFM69_lib import RFM69
import datetime
from handle_logging_lib import HandleLogging
import sys



class ReceivePackets:
    def __init__(self,moisture_callback):
        ''' start with an instance of the RFM69 radio and set the
        packet_received boolean to true.  This way, receive_begin
        will start in receive mode '''
        self._MOISTURE_INFO_PACKET            =   1
        self._MOISTURE_INFO_PACKET_RECEIVED   =   2
        self._TIME_INFO_PACKET                =   3
        self._TEST_PACKET                     =   4
        self._NO_PACKET_TYPE                  =   100
        self._ERROR_IN_PACKET_RECEIVED        =   99
        self._TEST_VALUE                      =   0x1234
        self.callback = moisture_callback
        self.radio =  RFM69()
        self.handle_logging = HandleLogging()
        self.handle_logging.print_info("Initializing ReceivePackets class.")
        self.node_id = None

    def _receive_done(self,packet):
        '''
        This function is called back when a packet is received.
        '''
        self.packet_list = list(packet)
        self.packet_type = self._NO_PACKET_TYPE
        try:
            self.packet_type = self.packet_list[0]
            self.node_id = self.packet_list[1]
        except IndexError as e:
            self.handle_logging.print_error(e)
        if self.packet_type == self._TEST_PACKET:
            self.handle_logging.print_info("Received a _TEST_PACKET from node {}.".format(self.node_id))
            packet_to_send = [self._TEST_PACKET]
            self.radio.send(bytearray(packet_to_send))
        elif self.packet_type == self._TIME_INFO_PACKET:
            self.handle_logging.print_info("Received a _TIME_INFO_PACKET from node {}.".format(self.node_id))
            # Send the current time and the watering hour.
            now = datetime.datetime.now()
            packet_to_send = [self._TIME_INFO_PACKET,  self.node_id,
                            now.hour, now.minute, now.second, self.watering_time]
            self.radio.send(bytearray(packet_to_send))

    def begin(self,watering_time=4):
        # Watering time is on a 24 hour clock.
        self.watering_time = watering_time
        self.radio.receive_begin(callback=self._receive_done)
