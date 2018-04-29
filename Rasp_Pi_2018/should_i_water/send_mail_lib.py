from datetime import datetime, date, time,timedelta
from handle_logging_lib impolrt HandleLogging
from reading_model import Reading,Node
import sys

###############

class SendMail:

    def __init__(self):
        ''' Get Ready to use the database containing moisture readings'''
        Reading.initialize()
        self.nodeID = None
        self.measurement = None
        self.battery_level = None
        self.handle_logging = HandleLogging(self.__class__.__name__)


    # get today's reading from the db
    def _get_todays_reading(self):
        '''
        Set the nodeID, measurement, and battery_level to today's reading.
        '''

        # We'll get the reading that should have been taken at 4AM today by
        # setting the filter from the beginning of the day to the time
        # it is right now.
        import pdb;pdb.set_trace()
        today_beginning = datetime.combine(date.today(), time())
        now = datetime.now()
        # While we expect just one reading for today...um...who knows?  Maybe there
        # will be multiple readings.  By adding get() we'll get the first one.
        try:
            #
            reading = Reading.get(Reading.timestamp.between(today_beginning,now))
            self.nodeID = reading.nodeID
            self.measurement = reading.measurement
            self.battery_level = reading.battery_level
            return True
        # no records exists for today....this isn't expected...
        except Reading.DoesNotExist as e:
            self.handle_logging.print_error(e)
            return False


    def get_moisture_puck_advice(self):
        if !self._get_todays_reading():
            self.handle_logging.print_error("Error - a reading does not exist.")
            return ''
        node_description="node" + str(self.nodeID)
        try:
            node_info = Node.get(Node.nodeID == self.nodeID)
            node_description = node_info.description
        except Node.DoesNotExist as e:
            self.handle_logging.print_error(e)
        if (self.measurement <= 205):
             return node_description+" - Unless the weather says otherwise, you should water."
        else:
             return node_description+" - No need to water today."

    def get_weather_png(self):
        pass

    def make_email(self):
        pass

    def send_email(self):
        pass
