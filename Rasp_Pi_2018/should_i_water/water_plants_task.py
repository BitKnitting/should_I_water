import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
sys.path.append(LIB_PATH)

from water_plants_lib import WaterPlants


###############
if __name__ == "__main__":
    water_plants = WaterPlants()
    water_plants.send_start_watering_packets()
