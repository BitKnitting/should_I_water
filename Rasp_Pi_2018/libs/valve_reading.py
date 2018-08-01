
from handle_logging_lib import HandleLogging
from reading_model import Valves
class ValveReading:

    def __init__():
        self.handle_logging = HandleLogging()

    def get_valves_info(self):
        '''
        Returns a list of tuples.  A tuple has the info contained within a
        row of the valves database. <valveID>,<moisturePuckID>,<wateringPuckID>,
        <watering_time>.  The length of the list = number of rows in the valves
        table.
        '''
        # Open the database based on the model defined in reading_model.py
        try:
            Valves.Initialize()
        except Valves.DoesNotExist as e:
                Valves.close()
                self.handle_logging.print_error(e)
                return None
