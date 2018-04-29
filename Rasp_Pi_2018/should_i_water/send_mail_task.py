#!/usr/bin/env python3

from send_mail_lib import SendMail

s = SendMail()
print( s.get_moisture_puck_advice())
print(s.get_weather())
