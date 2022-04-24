from .models import record_response, ResponseTypes
import smtplib
from urllib import response
from jinja2 import Template
from email.mime.text import MIMEText
from urllib.parse import urlencode
from datetime import datetime


class FakeSmtp:
    file = None
    counter = 0

    def sendmail(self, fromAddr, toAddr, msg):
        self.counter += 1
        with open('/tmp/mail{}.html'.format(self.counter), 'w') as file:
            # self.file.write('from: {} \n'.format(fromAddr))
            # self.file.write('to: {} \n'.format(toAddr))
            file.write(msg)

    def login(self, username, password):
        pass

    def starttls(self):
        pass


class EmailServer:
    """
    """
    smtp = None
    responseAddress = ""
    serverUsername = ""

    def __init__(self, responseAddress, type, serverAddress="", serverPort=587, serverUsername="", serverPassword=""):
        if type == 'smtp':
            self.smtp = smtplib.SMTP(serverAddress, serverPort)
        elif type == 'smtp_ssl':
            self.smtp = smtplib.SMTP(serverAddress, serverPort)
            self.smtp.starttls()
        elif type == 'test':
            self.smtp = FakeSmtp()
        else:
            print('Email provider not supported')
            raise Exception('Email provider not supported')
        print("Username: " + serverUsername + "Password: " + serverPassword)
        try:
            self.smtp.login(serverUsername, serverPassword)
            self.serverUsername = serverUsername
        except:
            print('smtp authentication failed')
            raise Exception('smtp authentication failed')
        self.responseAddress = responseAddress

    def getLink(self, hash, campaignId):
        params = {'s': hash, 'x': campaignId}
        return self.responseAddress + "gotphish?" + urlencode(params)

    def send_phish(self, fromAddr, toAddr,  subject, template, toAddrHash, campaignId):
        bodyText = Template(template).render(
            phishlink=self.getLink(toAddrHash, campaignId))
        message = MIMEText(bodyText, 'html')
        message['From'] = fromAddr
        message['Subject'] = subject
        message['To'] = toAddr
        msg = message.as_string()
        # add a record to keep track of the number of sent emails
        self.smtp.sendmail(self.serverUsername, toAddr, msg)
        record_response(toAddrHash, campaignId,datetime.utcnow(), ResponseTypes.SENT)

    def __del__(self):
        if self.smtp:
            self.smtp.quit()
