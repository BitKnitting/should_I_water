
import certifi
from datetime import datetime,timedelta
from handle_logging_lib import HandleLogging
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import urllib3

class PlotWeather:
    def __init__(self):
        self.handle_logging = HandleLogging()

    def get_weather_forecast(self):
        _NUMBER_OF_HOURS = 15
        '''
        Use the darksky weather service to get today's forecast.
        The 24 hour clock is used.  We pull out the probability of rain, the intensity of
        rain that will fall if it does rain, the cloud cover, and the temperature into a prediction_list.
        '''
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
        url = "https://api.darksky.net/forecast/d3fbc403cc28523a125c3c5ab8e43ded/47.649093,-122.199153"
        request = http.request('GET',url)
        # Try a five times in case there is a failure to connect
        for i in range(5):
            try:
                weather_prediction = json.loads(request.data.decode('utf8'))
            except HTTPError as e:
                weather_prediction = None
            else:
                prediction_data = weather_prediction['hourly']['data']
                first_hour = prediction_data[0]['time']
                last_hour = datetime.fromtimestamp(first_hour) + timedelta(hours=_NUMBER_OF_HOURS)
                prediction_list = []
                for hour_data in prediction_data:
                    hour_as_datetime = datetime.fromtimestamp(hour_data['time'])
                    int_hour = int(hour_as_datetime.strftime('%H'))
                    if hour_as_datetime >= last_hour or int_hour == 0:
                        return prediction_list
                    prediction_list.append([int_hour,hour_data['precipIntensity'],hour_data['precipProbability'],
                                           hour_data['cloudCover'],hour_data['temperature']])

    def plot_weather(self):
        '''
        Make a four plots: hour of the day (x-axis) vs probability of rain, intensity of rain,
        cloud cover, and temperature.  Each reading will be in it's own graph.
        store in PNG file.
        '''
        prediction_list = self.get_weather_forecast()
        # Set up the numpy array.
        array = np.array(prediction_list)
        # Set up the x-axis. The array's columns = hour, intensity, probability, cloud_cover, temperature.
        # The first hour is at location [0,0] and the last hour with readings is at the end of the first
        # column at [-1,0]
        start_hour = array[0,0].astype(int)
        end_hour = array[-1,0].astype(int)
        x = np.linspace(start_hour,end_hour,num=len(array))
        # set up the x-axis and y-axis data.
        hour = array[:,0].astype('int')
        intensity = array[:,1]
        probability = array[:,2]
        cloud_cover = array[:,3]
        temperature = array[:,4]
        # make room for 4 subplots.  We picked a size that looks good when the plot is saved as a png.
        fig, (ax1,ax2,ax3,ax4) = plt.subplots(nrows=4,figsize=(6,7))
        # The first plot will be the probability of rain.
        ax1.set_ylim([0,1])
        ax1.plot(hour,probability)
        ax1.set_ylabel('probability')
        ax1.set_title('Probability of rain',fontsize = 14)
        # The second plot will be the expected intensity of rain (assuming it rains at all).
        ax2.set_ylim([0,1])
        ax2.set_title('Rain Intensity',fontsize = 14)
        ax2.set_ylabel('intensity')
        ax2.plot(hour,intensity)
        # Plot the cloud cover
        ax3.set_ylim([0,1])
        ax3.set_title('Cloud Cover',fontsize = 14)
        ax3.set_ylabel('cloud cover')
        ax3.plot(hour,cloud_cover)
        # Plot the temperature
        ax4.set_xlabel('Hour (24 hour clock)',fontsize = 16)
        ax4.set_title('Temperature',fontsize = 14)
        ax4.set_ylabel('temperature')
        # Set the y - axis to fit the data within 10's.
        y_min = np.amin(temperature)
        rem = y_min % 10
        y_min -= rem
        y_max = np.amax(temperature)
        rem = y_max % 10
        y_max += (10-rem)
        ax4.set_ylim(y_min,y_max)
        ax4.plot(hour,temperature)
        # plt.tight_layout()
        # Adjust the layout
        fig.subplots_adjust(hspace=1)
        # Save as a png
        try:
            WEATHER_PNG = os.environ.get("WEATHER_PNG")
        except KeyError as e:
            handle_logging.print_error(e)
        else:
            fig.savefig(WEATHER_PNG)
            plt.close(fig)
