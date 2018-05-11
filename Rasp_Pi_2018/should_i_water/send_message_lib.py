#################################################################
# I want to send an email message to me and Thor.  The email message
# contains text as well as an image.  The email must be sent to gmail
# and outlook accounts.  I find it to be a bit confusing/complicated.
# The confusing comes with the "isms" gmail uses versus outlook to
# accept mail.  Also, it is a bit more complicated to send a message
# with an image.
#
# Author: Happyday Jonson    Copyright(c) 2018
######################################################################
# Import the libraries that will be used.
from apiclient.discovery import build
import base64
import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import httplib2
import mimetypes
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
import os
import smtplib



class SendMessage:
    def __init__(self):
        self.WEATHER_PNG = os.environ.get("WEATHER_PNG")
        today_string = datetime.datetime.now().strftime("%m/%d/%Y")
        self.subject_string = "Watering advice for {}".format(today_string)
    ############################################################
    def _create_MIME_message_with_attachment(self, sender, receiver, message_text, file):
        message = MIMEMultipart()
        message['to'] = receiver
        message['from'] = sender
        message['subject'] = self.subject_string
        msg = MIMEText(message_text)
        message.attach(msg)
        content_type, encoding = mimetypes.guess_type(file)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(file, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(file, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
        return message


    ######################################################################
    def _send_message_to_outlook(self, sender, receiver, message_text):
        server = smtplib.SMTP('smtp-mail.outlook.com',587)
        #server.set_debuglevel(1)
        server.starttls()
        OUTLOOK_USERNAME = os.environ.get("OUTLOOK_USERNAME")
        OUTLOOK_PASSWORD = os.environ.get("OUTLOOK_PASSWORD")
        server.login(OUTLOOK_USERNAME,OUTLOOK_PASSWORD)
        MIME_message = self._create_MIME_message_with_attachment(sender, receiver,
                        message_text, self.WEATHER_PNG)
        try:
            server.sendmail(MIME_message['From'], [MIME_message['To']],MIME_message.as_string())
        except SMTPDataError as e:
            print(e)
        server.quit()


    ##################################################################
    def _send_message_to_gmail(self, sender, receiver, message_text):
        def _authenticate():
            ''' gmail api goop to authenticate using oauth '''
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


        http = _authenticate()
        # Build the Gmail service from discovery
        gmail_service = build('gmail', 'v1', http=http)

        MIME_message = self._create_MIME_message_with_attachment(sender, receiver,
                         message_text, self.WEATHER_PNG)
        base64_message = {'raw': base64.urlsafe_b64encode(MIME_message.as_bytes()).decode()}
        try:
            gmail_service.users().messages().send(userId='me', body=base64_message).execute()
        except HTTPError as e:
            print(e)


    def send_message(self, receiver, message_text):
        ''' Send the message to either outlook or gmail.
        '''
        # Because of the way authentication works, the sender is
        # also the receiver
        sender = receiver
        if "outlook.com" in receiver or "msn.com" in receiver:
            self._send_message_to_outlook(sender, receiver, message_text)
        elif "gmail.com" in receiver:
            self._send_message_to_gmail(sender, receiver, message_text)
