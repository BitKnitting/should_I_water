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
import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
sys.path.append(LIB_PATH)
import datetime
from handle_logging_lib import HandleLogging
from RFM69_messages_lib import RFM69Messages
import sys



class ReceiveAndSendPackets(RFM69Messages):
    def __init__(self):
        super().__init__()
        self.handle_logging = HandleLogging()
        self.node_id = None
        self.packet_type = 0

    def _receive_done(self,packet):
        '''
        This function is called back when a packet is received.
        '''
        if not packet:
            self.handle_logging.print_error("Did not receive any bytes.")
            return
        self.packet_list = list(packet)
        self.packet_type = self.packet_list[0]
        # import pdb;pdb.set_trace()
        if (self.packet_type not in self.set_of_packet_types):
            self.handle_logging.print_info("Received a packet type, {}.  Not sure what this is".format(self.packet_list[0]))
            return
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

    def begin_recv_and_send(self,watering_time=4,keep_listening=True):
        # Watering time is on a 24 hour clock.
        self.watering_time = watering_time
        # This seems weird to me.  I pass in the named variable which is being
        # sent to another method in RFM69.
        # should_we_keep_listening = keep_listening
        self.radio.receive_begin(callback=self._receive_done,keep_listening=keep_listening)
