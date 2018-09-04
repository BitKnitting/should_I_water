import ast
import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
sys.path.append(LIB_PATH)

from water_plants_lib import WaterPlants


def get_input():
    on_or_off = ""
    while on_or_off != "on" and on_or_off != "off":
        on_or_off = input("Turn valves ON or OFF?: ").lower()
        if on_or_off != "on" and on_or_off != "off":
            print("Enter either on or off")

    while True:
        input_str = input("Enter valve(s), moisture puck id, or all: ").lower()
        try:
            if input_str == 'all':
                valves = True
            elif input_str.isdecimal():
                valves = int(input_str)
            elif '[' in input_str:
                valves = ast.literal_eval(input_str)
            break
        except TypeError as e:
            print("Uh oh...your entry was invalid...{}".format(e))
    return on_or_off, valves


###############
if __name__ == "__main__":
    on_or_off, valves = get_input()
    water_plants = WaterPlants()
    # 103 is assigned to the valve in the front
    # One or more valves is denoted by sending a list.
    if on_or_off == 'on':
        water_plants.send_start_watering_packets(valves)
    else:
        water_plants.send_stop_watering_packets(valves)
