import datetime
import inspect
import logging
import os
import sys
from datetime import datetime



class BaseClass:
    def __init__(self):
        LOGFILE = os.environ.get("LOGFILE")
        # set DEBUG for everything
        logging.basicConfig(filename=LOGFILE,level=logging.DEBUG)
        # matplotlib was clogging up the logfile.
        # From https://matplotlib.org/faq/troubleshooting_faq.html
        logger = logging.getLogger('matplotlib')
        # set WARNING for Matplotlib
        logger.setLevel(logging.WARNING)

class HandleLogging(BaseClass):

    def _get_caller_info(self):
        current_time = datetime.now().strftime('%b %-d %H:%M')
        # getting to the caller's caller since
        # this function is called from within
        # and we're interested in the 'ultimate' caller.
        (filename, line_number,
         name, lines, index) = inspect.getframeinfo(sys._getframe(2))
        return (current_time,filename, line_number, name)

    def print_error(self,message):
        (current_time, filename, line_number, name) = self._get_caller_info()
        logging.error('{} | {} | {} | {} : {}'.format(current_time,filename,line_number,name, message))

    def print_info(self,message):
        (current_time, filename,line_number,name) = self._get_caller_info()
        logging.info('{} | {} | {} | {}: {}'.format(current_time,filename,line_number,name, message))
