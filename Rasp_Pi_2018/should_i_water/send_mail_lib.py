import certifi
from datetime import datetime, date, time,timedelta
from handle_logging_lib import HandleLogging
from mail_providers_lib import GmailProvider,OutlookProvider
import json
from reading_model import Reading,Node
import sys
import urllib3

###############
_SUMMARY      =  1  # Return summary email message
_DETAILED     =  2  # Return detailed email message..

class SendMail:

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


    def _put_message_together(self,to_name='',weather=None,level_of_detail=_SUMMARY):
        ''' assemble the message to send in a morning email'''
        if len(to_name) > 0:
            message = "Good Morning, " +to_name+"!\n\n\n"
        else:
            message = "Good Morning!"    
        message += self.get_moisture_puck_advice(level_of_detail) + "\n\n"
        # Avoid multiple calls to get the weather...
        if weather is not None:
            message += weather + "\n\n"
        message += ("Please find many things to smile about."
                    "\n\nWith love,\nThor's little helper")
        return message


    def get_moisture_puck_advice(self,level_of_detail):
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
            if level_of_detail == _SUMMARY:
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
    ##########################################################################
    # can test with the following curl command:
    # curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X GET https://api.darksky.net/forecast/d3fbc403cc28523a125c3c5ab8e43ded/47.649093,-122.199153
    ##########################################################################
    def get_weather(self):
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
        url = "https://api.darksky.net/forecast/d3fbc403cc28523a125c3c5ab8e43ded/47.649093,-122.199153"
        request = http.request('GET',url)
        # Try a five times in case there is a failure to connect
        for i in range(5):
            try:
                weather_stuff = json.loads(request.data.decode('utf8'))
                return weather_stuff['hourly']['summary']
            except HTTPError as e:
                self.handle_logging.print_error(e)
        return "Sorry about this.  The elves refuse to get today's forecast."

    def get_battery_level(self):
        if self._is_a_reading():
            return "The battery level is at {}V.".format(self.battery_level)
        return "Unable to get today's battery level reading."

    def send_email(self):
        weather = self.get_weather()
        message = self._put_message_together('Thor',weather,_SUMMARY)
        thor_mail = OutlookProvider()
        thor_mail.send_mail('thor_johnson@msn.com',message)
        message = self._put_message_together('Margaret',weather,_DETAILED)
        me_mail = GmailProvider()
        me_mail.send_mail('happyday.mjohnson@gmail.com',message)
