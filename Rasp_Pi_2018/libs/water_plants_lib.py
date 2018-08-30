from moisture_reading_lib import MoistureReading
from reading_model import Valves
from RFM69_messages_lib import RFM69Messages
import time


class WaterPlants(MoistureReading, RFM69Messages):
    '''
    Turn on and off watering valves.  This is a
    subclass of MoistureReading to autowater based on the moisture
    readings of the moisture pucks.  Alternitively, we can water
    whenever we want.
    '''

    def __init__(self):
        '''start receiving/sending packets to watering pucks'''
        super().__init__()

    def _get_valves(self, all_valves=True):
        '''
        Return a list of valves from the valves table.  Which rows are returned
        depend on all_values.  all_values can be:
        True - if all values is True, all rows in the valves table are returned.
           e.g.:  self._get_valves(True)
        An int - the rows whose moisture puck id are = to the int are returned.
           e.g.:  self._get_valves(1)
        Returns a list of valves that have the valve ID in the all_values list.
           e.g.:  self._get_values([102,102])

        Each entry in the list of valves is a tuple:
            (wateringPuckID,valveID,watering_time)
        '''
        valves_list = []
        try:
            Valves.initialize()
            if all_valves is True:
                # Peewee's .dicts() explanation: http://docs.peewee-orm.com/en/latest/peewee/querying.html?highlight=dicts()#retrieving-row-tuples-dictionaries-namedtuples
                query = Valves.select().dicts()
            elif isinstance(all_valves, int):
                query = Valves.select().dicts().where(Valves.moisturePuckID == all_values)
            elif isinstance(all_valves, list):
                query = Valves.select().dicts().where(Valves.valveID.in_(all_valves))
            # The watering puck id tells us which watering puck to send the rfm69
            # message to.  The message will contain the valve ID.  This way, the
            # watering puck knows which valve to turn on and off.
            for row in query:
                valves_list.append((row['wateringPuckID'], row['valveID'], row['watering_time']))
            Valves.close()
            return valves_list
        except Valves.DoesNotExist as e:
            Valves.close()
            self.handle_logging.print_error(e)
            return []

    def send_start_watering_packets(self, all_valves=True):
        '''
        Send a start watering packet to a watering puck for each valve.
        Which watering pucks and which valves are determined by the all_values
        parameter:
        - all_valves = True: loops through all entries in the valves table (i.e.:
        all valves regardless of watering puck)
        - all_valves = moisture puck ID:  All valves that are identified as being
        "managed" by a particular moisture puck.  For example, the valves table has
        a column for the moisture puck id.  The rows with the moisture puck ID passed
        in will be sent a start watering packet.
        - all_valves = list of valves (e.g.:[102,102]) valves identified by the valveID
        column in the valves table will be sent a start watering packet.
        with id 2 for 30 minutes.
        '''
        # Each entry in valves_list is a tuple (valveID, wateringPuckID,
        # watering_time).
        # The info is needed to know which watering puck to send the
        # start watering packet to and which valve to open/close.
        valves_list = self._get_valves(all_valves)
        if not valves_list:
            return

        for item in valves_list:
            # Put the packet together in the expected format.
            packet_to_send = [self._START_WATERING_PACKET,  item[0], item[1], item[2]]
            # Send the packet
            self.handle_logging.print_info(("sending packet: watering puck: {}, "
                                            "valve id: {}, minutes to water: {}").format(item[0], item[1], item[2]))
            self.radio.send(bytearray(packet_to_send))
            self.handle_logging.print_info(
                "sent packet. Waiting {} minutes to send next packet".format(item[2]))
            time.sleep(item[2]*60)

    def begin_water_if_needed(self, nodeID, measurement):
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
                self.send_start_watering_packets(all_valves=False)
