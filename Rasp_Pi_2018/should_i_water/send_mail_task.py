#!/usr/bin/env python3

from build_message_lib import BuildMessage
from send_message_lib import SendMessage

b = BuildMessage()
# send margaret a message.  False means send detailed data.
m = b.build_message('Margaret',False)
s = SendMessage()
s.send_message('happyday.mjohnson@gmail.com',m)
m = b.build_message('Thor',True)  # Send summary info
s.send_message('thor_johnson@msn.com',m)
