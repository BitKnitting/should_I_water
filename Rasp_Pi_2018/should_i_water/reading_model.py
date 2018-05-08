from peewee import *
import datetime
from handle_logging_lib import HandleLogging
import os
import sys

handle_logging = HandleLogging()
try:
   DATABASE_FILE = os.environ.get("DATABASE_FILE")
except KeyError as e:
   handle_logging.print_error(e)
   sys.exit(1)



db = SqliteDatabase("DATABASE_FILE")

class BaseModel(Model):
    def initialize():
        '''Create the database and the table if they don't exist.'''
        db.connect()
        db.create_tables([Reading,Node],safe=True)
    class Meta:
        database = db

class Reading(BaseModel):
    nodeID = IntegerField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    measurement = IntegerField()
    battery_level = FloatField()

class Node(BaseModel):
    nodeID = IntegerField()
    description = CharField(max_length=255)
    threshold = IntegerField()
