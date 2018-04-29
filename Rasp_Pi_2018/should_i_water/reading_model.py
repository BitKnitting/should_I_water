from peewee import *
import datetime



db = SqliteDatabase('/home/pi/myLadybugHelper/databases/garden_readings.db')
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
