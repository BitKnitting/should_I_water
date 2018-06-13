
from datetime import datetime, date, time,timedelta
from handle_logging_lib import HandleLogging
from reading_model import Reading,MoisturePucks,Valves

class MoistureReading:
    # TODO: Handle multiple moisture pucks.  Right now everything focuses on
    # having just 1.
    '''Get reading and moisture puck info from the garden_readings.db.'''
    def __init__(self):
        super().__init__()
        self.moisture_puck_id = None
        self.measurement = None
        self.battery_level = None
        self.handle_logging = HandleLogging()
    # get today's reading from the db
    def is_a_reading(self):
        '''
        See if there is a moisture reading for today.  If there is, assign the
        readings to the moisture_puck_id, measurement, and battery level.
        These properties are then used by other methods within this class.
        '''

        # We'll get the reading that should have been taken at 4AM today by
        # setting the filter from the beginning of the day to the time
        # it is right now.
        today_beginning = datetime.combine(date.today(), time())
        now = datetime.now()
        # While we expect just one reading for today...um...who knows?  Maybe there
        # will be multiple readings.  By adding get() we'll get the first one.
        try:
            Reading.initialize()
            reading = Reading.get(Reading.timestamp.between(today_beginning,now))
            Reading.close()
            self.moisture_puck_id = reading.nodeID
            self.measurement = reading.measurement
            self.battery_level = reading.battery_level
            return True
        # no records exists for today....this isn't expected...
        except Reading.DoesNotExist as e:
            Reading.close()
            self.handle_logging.print_error(e)
            return False

    def get_moisture_puck_info(self,moisture_puck_id = None):
        '''
        The most important piece of information in the moisture puck info
        is the threshold value.  The threshold value is compared against
        the measurement to figure out whether that plants in the moisture
        puck's area need watering.
        '''
        if not moisture_puck_id:
            moisture_puck_id = self.moisture_puck_id
        try:
            MoisturePucks.initialize()
            node_info = MoisturePucks.get(MoisturePucks.nodeID == moisture_puck_id)
            MoisturePucks.close()
            return node_info
        except MoisturePucks.DoesNotExist as e:
            MoisturePucks.close()
            self.handle_logging.print_error(e)
            return None
