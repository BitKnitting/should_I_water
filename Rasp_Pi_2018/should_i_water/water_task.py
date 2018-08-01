###
import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
sys.path.append(LIB_PATH)
from RFM69_messages_lib import RFM69Messages
'''
Sequentially water each node that is in the valves table.  We sequentially
water to prevent low water pressure if multiple valves share the same
starting hose.
'''
######################################################################################
if __name__ == "__main__":
    # Go through the records in the garden_readings.db valves table.  Each
    # reading gives info on a valve that waters an area of the garden.
    # i.e.: the columns of valve =
    # id = id is assigned by sqlite3 when the record is added.
    # valveID = id assigned to the mcu pin that turns on/off the valve
    # wateringPuckID = node id of the RFM69 Feather.
    # description ...
    # watering_time = the number of minutes to water.

    try:
        # Go
        valve_id,on_or_off,watering_minutes = getInput()
        rf69 = RFM69Messages()
        watering_puck_node_id = 4
        if on_or_off == 'on':
            packet_to_send = [rf69._START_WATERING_PACKET, watering_puck_node_id, valve_id, watering_minutes]
        else:
            packet_to_send = [rf69._STOP_WATERING_PACKET,watering_puck_node_id,valve_id]
        rf69.radio.send(bytearray(packet_to_send))
        rf69.radio.receive_begin(keep_listening=False, callback= receive_done)
    except (Need3InputError,UnknownValveError,UnknownOnOffError,WateringTimeTooLongError) as e:
        print("\n*****************************************\n")
        print(e)
        print("\n*****************************************\n")
