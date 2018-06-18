
import certifi
from handle_logging_lib import HandleLogging
import json
from moisture_reading_lib import MoistureReading
import urllib3


class BuildMessage(MoistureReading):
    '''
    Build a message about the status of the plants - do they need watering
    or not - and provide a summary report on the weather.
    '''

    def _put_message_together(self,to_name='',weather=None,summary_message=True):
        ''' assemble the message to send in a morning email'''
        if len(to_name) > 0:
            message = "Good Morning, " +to_name+"!\n\n\n"
        else:
            message = "Good Morning!"
        message += self.get_moisture_puck_advice(summary_message) + "\n\n"
        # Avoid multiple calls to get the weather...
        if weather is not None:
            message += weather + "\n\n"
            message += ('I put together more detailed weather info.  You can '
                        'click on the iddy-biddy image to make it bigger.')
        message += ("\n\nPlease find many things to smile about."
                    "\n\nWith love,\nThor's little helper")
        return message

    def get_moisture_puck_advice(self,summary_message):
        '''get today's reading and then get the text description for
        the node id'''
        # If we didn't get a reading, we don't know what moisture puck id we're
        # working with.
        if self.is_a_reading():
            node_info = self.get_moisture_puck_info()
            if node_info == None:
                return ' '
            if summary_message:
                reading_details = ""
            else:
                reading_details = (" The reading is {}, the threshold is {}, "
                            "the battery level is {}."
                            .format(self.measurement,node_info.threshold,self.battery_level))
            if self.measurement < node_info.threshold:
                return node_info.description+" - Unless the weather says otherwise, you should water."+ reading_details
            else:
                return node_info.description+" - No need to water today." + reading_details

                return node_info.description+" - No need to water today."
        else:
            return "Well that stinks.  Unfortunately, there are no moisture readings for today!"


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
