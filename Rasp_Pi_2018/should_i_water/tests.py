# TBD - unit tests.....

import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
sys.path.append(LIB_PATH)

import unittest
from moisture_reading_lib import MoistureReading

class MoistureReadingTests(unittest.TestCase):
    def setUp(self):
        self.moisture_reading = MoistureReading()

    def test_is_a_reading(self):
        self.assertTrue(self.moisture_reading.is_a_reading())



if __name__ == '__main__':
    unittest.main()
