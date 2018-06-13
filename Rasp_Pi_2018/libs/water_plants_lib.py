from moisture_reading_lib import MoistureReading
from reading_model import Valves
from RFM69_messages_lib import RFM69Messages


class WaterPlants(MoistureReading,RFM69Messages):
    '''
    Turn on and off valves if the plants need watering.  This is a
    subclass of MoistureReading because in order to know whether to water,
    we first need to find out if there is a reading.  If there is a reading,
    we need to check if it is below the value set for the moisture puck's threshold.
    '''
    def __init__(self):
        '''start receiving/sending packets to watering pucks'''
        super().__init__()


    def _get_valves(self):
        '''
        Returns a list of (valveID,wateringPuckID) tuples.  One for each valve
        associated with the moisture puck.
        '''
        valves_list = []
        try:
            Valves.initialize()
            query = Valves.select().dicts().where(Valves.moisturePuckID == self.moisture_puck_id)
            # The watering puck id tells us which watering puck to send the rfm69
            # message to.  The message will contain the valve ID.  This way, the
            # watering puck knows which valve to turn on and off.
            for row in query:
                valves_list.append( (row['wateringPuckID'],row['valveID'],row['watering_time']) )
            Valves.close()
            return valves_list
        except Valves.DoesNotExist as e:
            Valves.close()
            self.handle_logging.print_error(e)
            return []
    def send_start_watering_packets(self,valves_list):
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
            # Send the packet
            self.radio.send(bytearray(packet_to_send))
    def begin_water_if_needed(self,nodeID,measurement):
        '''
        Check the moisture puck readings.  If a reading is below the threshold,
        work with the valve to turn it on/off (i.e.: water the plants)
        '''
        # By calling is a reading, we'll get the moisture puck id...


        if self.is_a_reading():
            # Get the threshold value to compare the reading against.
            node_info = self.get_moisture_puck_info()
            # Is the moisture reading saying it's dryer than we want?
            # TEST
            self.measurement = 0
            if self.measurement < node_info.threshold:
                # Each entry in valves_list is a tuple (valveID, wateringPuckID,
                # watering_time).
                # The info is needed to know which watering puck to send the
                # start watering packet to and which valve to open/close.
                valves_list = []
                valves_list = self._get_valves()

                if not valves_list:
                    return
                self.send_start_watering_packets(valves_list)
