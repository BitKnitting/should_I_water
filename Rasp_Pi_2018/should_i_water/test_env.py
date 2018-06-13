import os

pwd = os.environ['OUTLOOK_USERNAME']
print('OUTLOOK_USERNAME: {}',format(pwd))
db_file = os.environ["DATABASE_FILE"]
print("DATABASE FILE: {}".format(db_file))
