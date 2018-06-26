import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
sys.path.append(LIB_PATH)
from receive_and_send_packets_lib import ReceiveAndSendPackets
from moisture_reading_lib import MoistureReading
from reading_model import Reading,Valves
import struct
import time

class HandleMoisturePackets(ReceiveAndSendPackets,MoistureReading):
    def _store_measurement(self,measurement,battery_level):
        try:
            battery_level = round(battery_level,2)
            # Use time's default value.
            Reading.initialize()
            Reading.create(nodeID=self.node_id,measurement=measurement,
                     battery_level=battery_level)
            Reading.close()
            self.handle_logging.print_info('Measurement stored.  nodeID: {}, measurement: {}, battery_level: {}'
                    .format(self.node_id,measurement,battery_level))
        except ValueError as e:
            self.handle_logging.print_error(e.message)

    def _water_if_needed(self,measurement):
        def _get_valves():
            '''
            Returns a list of (valveID,wateringPuckID) tuples.  One for each valve
            associated with the moisture puck.
            '''
            valves_list = []
            try:
                Valves.initialize()
                query = Valves.select().dicts().where(Valves.moisturePuckID == self.node_id)
                # The watering puck id tells us which watering puck to send the rfm69
                # message to.  The message will contain the valve ID.  This way, the
                # watering puck knows which valve to turn on and off.
                for row in query:
                    valves_list.append( (row['wateringPuckID'],row['valveID'],row['watering_time']) )
                Valves.close()
                return valves_list
            except Valves.DoesNotExist as e:
                Valves.close()
                self.handle_logging.print_error(e.message)
                return []
        def _send_start_watering_packets(valves_list):
            '''
            Send a start watering packet to the watering puck that is responsible
            for watering the area where the moisture puck's reading was below the
            threshold value.  The values parameter is a list of tuples that contain
            the id of the watering puck, the valve id, and the watering time.
            E.g.: [(1,1,15),(1,2,30)] says to send a start watering packet to the
            watering puck whose node id = 1.  The watering puck should turn on the valve
            identified as 1 for 15 minutes.  The second tuple says to send another
            packet to the same watering puck, this time telling it to turn on the valve
            with id 2 for 30 minutes.
            '''
            for item in valves_list:
                # Put the packet together in the expected format.
                packet_to_send = [self._START_WATERING_PACKET,  item[0],item[1],item[2]]
                self.handle_logging.print_info("Waiting 25 seconds")
                time.sleep(25) # Give a bit of time to the RFM69 chip...I was
                               # not receiving packets...
                # Send the packet
                self.radio.send(bytearray(packet_to_send))
                self.handle_logging.print_info("Sent start watering packet to node {}, valve {}.  Water for {} minutes".format(item[0],item[1],item[2]))

        #########################################################################
        # Get the threshold value to compare the reading against.
        node_info = self.get_moisture_puck_info(self.node_id)
        # Is the moisture reading saying it's dryer than we want?
        # TEST

        if measurement < node_info.threshold:
            self.handle_logging.print_info("Watering.  The measurement ({}) is less than the threshold ({}).".format(measurement,node_info.threshold))
            # Each entry in valves_list is a tuple (valveID, wateringPuckID,
            # watering_time).
            # The info is needed to know which watering puck to send the
            # start watering packet to and which valve to open/close.
            valves_list = []
            valves_list = _get_valves()
            # There might be no valves in the list if the area covered by the
            # moisture puck doesn't include auto irrigation.
            if not valves_list:
                return
            _send_start_watering_packets(valves_list)
        else:
            self.handle_logging.print_info("No need to water. The measurement ({}) is greater than or equal to the threshold ({}).".format(measurement,node_info.threshold))

    def _receive_done(self,packet):
        super()._receive_done(packet)
        if self.packet_type == self._MOISTURE_INFO_PACKET:
            self.handle_logging.print_info("Received a _MOISTURE_INFO_PACKET from node {}.".format(self.node_id))
            packet_to_send = [self._MOISTURE_INFO_PACKET,self.node_id]
            self.radio.send(bytearray(packet_to_send))
            try:
                # Take care to strip out the packet type and node id.
                measurement,battery_level = struct.unpack('=hf',packet[2:])
                battery_level = round(battery_level,2)
                self._store_measurement(measurement,battery_level)
                self._water_if_needed(measurement)
            except struct.error as e:
                self.handle_logging.print_error(e.message)
                packet_to_send = [self._ERROR_IN_PACKET_RECEIVED,self.node_id]
                self.radio.send(bytearray(packet_to_send))
