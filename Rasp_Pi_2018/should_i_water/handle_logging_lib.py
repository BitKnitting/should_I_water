import datetime
import inspect
import logging
import os
import sys

LOGFILE = os.environ.get("LOGFILE")
logging.basicConfig(filename=LOGFILE,level=logging.DEBUG)

class BaseClass:
    def __init__(self):
        self.date_and_time = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")

class HandleLogging(BaseClass):

    def _get_caller_info(self):
        # getting to the caller's caller since
        # this function is called from within
        # and we're interested in the 'ultimate' caller.
        (filename, line_number,
         name, lines, index) = inspect.getframeinfo(sys._getframe(2))
        return (filename, line_number, name)

    def print_error(self,message):
        (filename,line_number,name) = self._get_caller_info()
        logging.error('{} | {} | {} | {} : {}'.format(self.date_and_time,
        filename,line_number,name, message))

    def print_info(self,message):
        (filename,line_number,name) = self._get_caller_info()
        logging.info('{} | {} | {} | {}: {}'.format(self.date_and_time,
        filename,line_number,name, message))
