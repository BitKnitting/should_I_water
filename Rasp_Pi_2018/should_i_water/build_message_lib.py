import certifi
from datetime import datetime, date, time,timedelta
from handle_logging_lib import HandleLogging
import json
from reading_model import Reading,Node
import urllib3


class BuildMessage:
    def __init__(self):
        ''' Get Ready to use the database containing moisture readings'''
        Reading.initialize()
        self.nodeID = None
        self.measurement = None
        self.battery_level = None
        self.handle_logging = HandleLogging()


    # get today's reading from the db
    def _is_a_reading(self):
        '''
        Set the nodeID, measurement, and battery_level to today's reading.
        '''

        # We'll get the reading that should have been taken at 4AM today by
        # setting the filter from the beginning of the day to the time
        # it is right now.
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

    def _put_message_together(self,to_name='',weather=None,summary_message=True):
        ''' assemble the message to send in a morning email'''
        if len(to_name) > 0:
            message = "Good Morning, " +to_name+"!\n\n\n"
        else:
            message = "Good Morning!"
        import pdb;pdb.set_trace()
        message += self.get_moisture_puck_advice(summary_message) + "\n\n"
        # Avoid multiple calls to get the weather...
        if weather is not None:
            message += weather + "\n\n"
        message += ("Please find many things to smile about."
                    "\n\nWith love,\nThor's little helper")
        return message

    def get_moisture_puck_advice(self,summary_message):
        '''get today's reading and then get the text description for
        the node id'''
        if self._is_a_reading():
            node_description="node" + str(self.nodeID)
            try:
                node_info = Node.get(Node.nodeID == self.nodeID)
                node_description = node_info.description
                node_threshold = node_info.threshold
            except Node.DoesNotExist as e:
                self.handle_logging.print_error(e)
            import pdb;pdb.set_trace()
            if summary_message:
                reading_details = ""
            else:
                reading_details = (" The reading is {}, the threshold is {}, "
                            "the battery level is {}."
                            .format(self.measurement,node_threshold,self.battery_level))
            if (self.measurement <= node_threshold):
                return node_description+" - Unless the weather says otherwise, you should water."+ reading_details
            else:
                return node_description+" - No need to water today." + reading_details

                return node_description+" - No need to water today."
        else:
            self.handle_logging.print_error("Error - a reading does not exist.")
            return ''


    def get_weather(self):
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
        url = "https://api.darksky.net/forecast/d3fbc403cc28523a125c3c5ab8e43ded/47.649093,-122.199153"
        request = http.request('GET',url)
        # Try a five times in case there is a failure to connect
        for i in range(5):
            try:
                weather_stuff = json.loads(request.data.decode('utf8'))
                return weather_stuff['hourly']['summary']
            except urllib3.HTTPError as e:
                self.handle_logging.print_error(e)
        return "Sorry about this.  The elves refuse to get today's forecast."

    def get_battery_level(self):
        if self._is_a_reading():
            return "The battery level is at {}V.".format(self.battery_level)
        return "Unable to get today's battery level reading."


    def build_message(self,to_name='',summary_message = True):
        # Avoid multiple calls to the weather API.
        weather = self.get_weather()
        message = self._put_message_together(to_name, weather, summary_message)
        return(message)
