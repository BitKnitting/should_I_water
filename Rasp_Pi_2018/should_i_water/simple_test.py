import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
sys.path.append(LIB_PATH)

import unittest
from moisture_reading_lib import MoistureReading

moisture_reading = MoistureReading()
node_info = moisture_reading.get_moisture_puck_info(1)
