import os
import smtplib
from email.mime.text import MIMEText



msg = MIMEText('this is a test message')
msg['Subject'] = 'subject of message'
msg['To'] = 'thor_johnson@msn.com'
msg['From'] = 'thor_johnson@msn.com'

try:
   server = smtplib.SMTP('smtp-mail.outlook.com',587)
   server.set_debuglevel(1)
   server.starttls()
   server.login(os.environ.get("USERNAME"),os.environ.get("PASSWORD"))
   server.sendmail(msg['From'], [msg['To']], msg.as_string())
   server.quit()
   print "Successfully sent email"
except smtplib.SMTPException as error_details:
   print "Error: unable to send email.  Error message: ",error_details
