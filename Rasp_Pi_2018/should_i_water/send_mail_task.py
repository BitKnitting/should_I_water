#!/usr/bin/env python3

from build_message_lib import BuildMessage
from plot_weather_lib import PlotWeather
from send_message_lib import SendMessage
# TODO: Error checking needs improvement.
# plot_weather() returns True (could create a PNG) or False (PNG of weather
# could not be created).  Yet, build message assumes multiplart MIME with the
# Weather PNG in place.
p = PlotWeather()
b = BuildMessage()
# send margaret a message.  False means send detailed data.
m = b.build_message('Margaret',False)
s = SendMessage()
s.send_message('happyday.mjohnson@gmail.com',m)
m = b.build_message('Thor',True)  # Send summary info
s.send_message('thor_johnson@msn.com',m)
