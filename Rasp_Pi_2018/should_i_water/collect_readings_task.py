#!/usr/bin/env python3

from receive_moisture_packets_lib import ReceiveMoisturePackets
from handle_logging_lib import HandleLogging
from reading_model import Reading

handle_logging = HandleLogging()


def store_measurement(nodeID,measurement,battery_level):
    '''
    Callback fires from collect_readings_lib when receive a measurement.
    stores the reading from the Feather moisture sensor.  The date/time
    is defaulted - see the database definition.
    '''
    try:
        battery_level = round(battery_level,2)
        # Use time's default value.
        Reading.initialize()
        Reading.create(nodeID=nodeID,measurement=measurement,
                 battery_level=battery_level)
        Reading.close()
        handle_logging.print_info('Measurement stored.  nodeID: {}, measurement: {}, battery_level: {}'
                .format(nodeID,measurement,battery_level))
    except ValueError as e:
        handle_logging.print_error(e)



###############
if __name__ == "__main__":
    moisture_packet = ReceiveMoisturePackets(store_measurement)
    moisture_packet.begin()
