###
import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
sys.path.append(LIB_PATH)
from RFM69_messages_lib import RFM69Messages
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
_YELLOW_VALVE                    =   100
_GREEN_VALVE                     =   101
_BLUE_VALVE                      =   102
#######################################################################
# INPUT CHECK
class Need3InputError(Exception):
    def __str__(self):
        return ("I need 3 pieces of info separated by commas: "
         "which valve (blue,yellow, or green), whether to turn "
         "the valve on or off, the watering minutes.\n"
         "E.G.: blue,on,15 or blue,off,0\n"
         "If turning the valve off, the watering minutes are ignored.")

class UnknownValveError(Exception):
    def __str__(self):
        return ("I didn't recognize the first variable as a valve type. "
        "The valves I know about are blue, green, yellow \n"
         "E.G.: yellow,off,0")

class UnknownOnOffError(Exception):
    def __str__(self):
        return ("The second variable must be on or off.\n "
             "E.G.: green,on,20")

class WateringTimeTooLongError(Exception):
    def __str__(self):
        return ("The watering time must be between 0 and 50 minutes.\n "
             "E.G.: green,on,20")

def getInput():
    input_str = input("Enter valve, on or off, watering minutes: ").lower()
    input_list = input_str.split(',')
    if len(input_list) != 3:
        raise Need3InputError
    if input_list[0] != 'blue' and input_list[0] != 'yellow' and input_list[0] != 'green':
        raise UnknownValveError
    valve_id = _BLUE_VALVE
    if input_list[0] == 'yellow':
        valve_id = _YELLOW_VALVE
    if input_list[0] == 'green':
        valve_id = _GREEN_VALVE
    if input_list[1] != 'on' and input_list[1] != 'off':
        raise UnknownOnOffError
    try:
        watering_time = int(input_list[2])
    except ValueError:
        raise WateringTimeTooLongError
    if watering_time < 0 or watering_time > 50:
        raise WateringTimeTooLongError
    return valve_id,input_list[1],watering_time
def receive_done(packet):
    print("received packet {}".format(packet))
######################################################################################
if __name__ == "__main__":
    try:
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
