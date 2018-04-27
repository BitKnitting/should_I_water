#!/usr/bin/env python3
import datetime
from lib.collect_readings_lib import Measurement
from peewee import *

db = SqliteDatabase('/home/pi/RFM69_Pi/garden_readings.db')

##########################
class Reading(Model):
    nodeID = IntegerField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    measurement = IntegerField()
    battery_level = FloatField()

    class Meta:
        database = db
##########################
def print_error(self,e):
    '''Interesting goo to print out when an error happens...'''
    logging.error('{},{}:{}'.format(self.__class__.__name__,
            sys._getframe().f_code.co_name,e))


def store_measurement(nodeID,measurement,battery_level):
    '''
    Callback fires from collect_readings_lib when receive a measurement.
    stores the reading from the Feather moisture sensor.  The date/time
    is defaulted - see the database definition.
    '''
    try:
        battery_level = round(battery_level,2)
        # Use time's default value.
        Reading.create(nodeID=nodeID,measurement=measurement,
                 battery_level=battery_level)
        print('measurement stored.  nodeID: {}, measurement: {}, battery_level: {}'
                .format(nodeID,measurement,battery_level))
    except ValueError as e:
        self.print_error(e)


def initialize():
    '''Create the database and the table if they don't exist.'''
    db.connect()
    db.create_tables([Reading],safe=True)
###############
if __name__ == "__main__":
    initialize()
    measurement = Measurement(store_measurement)
    measurement.begin()
