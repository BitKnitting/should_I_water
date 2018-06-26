
import inspect
import logging
import os
import sys

class HandleLogging:

    def __init__(self):
        LOGFILE = os.environ.get("LOGFILE")
        # set DEBUG for everything
        # In the docs: https://docs.python.org/3/library/logging.html
        # 16.6.7 Talks about LogRecord Attributes.  I am using this to
        # provide date/time info...i tried a few others to get stack
        # info, however returned info on this module.  So used inspect.
        logging.basicConfig(filename=LOGFILE,level=logging.DEBUG,
        format='%(asctime)s %(levelname)s  %(message)s',
        datefmt='%b %-d,%Y %H:%M')
        # matplotlib was clogging up the logfile.
        # From https://matplotlib.org/faq/troubleshooting_faq.html
        logger = logging.getLogger('matplotlib')
        # set WARNING for Matplotlib
        logger.setLevel(logging.WARNING)
        # Also turn off peewee's debug logging lines
        # See http://peewee.readthedocs.io/en/latest/peewee/database.html#logging-queries
        logger = logging.getLogger('peewee')
        logger.setLevel(logging.WARNING)

    def _make_full_message(self,message):
        # getting to the caller's caller since
        # this function is called from within
        (filepathname, line_number,
         name, lines, index) = inspect.getframeinfo(sys._getframe(2))
        code_info_str = ": {} - {} - {} : ".format(os.path.basename(filepathname), line_number, name)
        return (code_info_str + message)

    def print_error(self,message):
        logging.error(self._make_full_message(message))

    def print_info(self,message):
        logging.info(self._make_full_message(message))
