#!/usr/bin/python

import httplib2

from apiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser
from email.encoders import encode_base64
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from handle_logging_lib import HandleLogging
import datetime
import base64
import os

class MailProviders:
    def __init__(self):
        self.handle_logging = HandleLogging()
        today_string = datetime.datetime.now().strftime("%m/%d/%Y")
        self.subject_string = "Watering advice for {}".format(today_string)


    def _create_message(self,sender, to, subject, message_text):
        """Create a message for an email.
        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        text = MIMEText(message_text)
        message.attach(text)
        WEATHER_PNG = os.environ.get("WEATHER_PNG")
        with open(WEATHER_PNG, 'rb') as fp:
            weather_image = MIMEImage(fp.read(), _subtype='png')
            import pdb;pdb.set_trace()
        message.attach(weather_image)
        # UGH!  See:
        # https://stackoverflow.com/questions/43352496/gmail-api-error-from-code-sample-a-bytes-like-object-is-required-not-str
        # return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}



class GmailProvider(MailProviders):
    """send gmail"""

    def _authenticate(self):

        # Path to the client_secret.json file downloaded from the Developer Console
        CLIENT_SECRET_FILE = os.environ.get("CLIENT_SECRET_FILE")
        # Check https://developers.google.com/gmail/api/auth/scopes
        # for all available scopes
        # OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
        OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.send'
        # Location of the credentials storage file
        GMAIL_STORAGE = os.environ.get("GMAIL_STORAGE")
        STORAGE = Storage(GMAIL_STORAGE)

        # Start the OAuth flow to retrieve credentials
        flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
        http = httplib2.Http()

        # Try to retrieve credentials from storage or run the flow to generate them
        credentials = STORAGE.get()
        if credentials is None or credentials.invalid:
            args = argparser.parse_args()
            args.noauth_local_webserver = True
            credentials = tools.run_flow(flow, STORAGE, args, http=http)
        # Authorize the httplib2.Http object with our credentials
        return credentials.authorize(http)






    def _send_gmail(self,service, user_id, message):
        """Send an email message.
        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.

        Returns:
          Sent Message.
        """
        try:
            message = (service.users().messages().send(userId=user_id, body=message)
                .execute())
            info_string = "Message sent. ID = {}".format(message['id'])
            self.handle_logging.print_info(info_string)
            return message
        except HttpError as e:
            self.handle_logging.print_error(e)

    ###########################################################################
    def send_mail(self,to_string,message_string):
        http = self._authenticate()

        # Build the Gmail service from discovery
        gmail_service = build('gmail', 'v1', http=http)

        # Create message

        message = self._create_message(to_string,
                                       to_string,
                                       self.subject_string, message_string)
        # Send message
        self._send_gmail(gmail_service, 'me', message)

class OutlookProvider(MailProviders):
    '''send mail to outlook'''

    def send_mail(self,to_string,message_string):
        msg = self._create_message(to_string,
                                   to_string,
                                   self.subject_string,
                                   message_string)

        try:
           server = smtplib.SMTP('smtp-mail.outlook.com',587)
           # server.set_debuglevel(1)
           server.starttls()
           server.login(os.environ.get("OUTLOOK_USERNAME"),os.environ.get("OUTLOOK_PASSWORD"))
           server.sendmail(msg['From'], [msg['To']], msg.as_string())
           server.quit()
           self.handle_logging.print_info('Outlook email successfully sent')
        except smtplib.SMTPException as e:
           self.handle_logging.print_error(e)
