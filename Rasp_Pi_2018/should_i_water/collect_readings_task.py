#!/usr/bin/env python3
import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
sys.path.append(LIB_PATH)
from handle_moisture_packets_lib import HandleMoisturePackets



###############
if __name__ == "__main__":
    moisture_packet = HandleMoisturePackets()
    moisture_packet.begin_recv_and_send()
