import smtplib
from urllib import response
from jinja2 import Template
from email.mime.text import MIMEText


class FakeSmtp:
    file = None

    def __init__(self):
        self.file = open('tmp/sent.txt', 'w')

    def sendmail(self, fromAddr, toAddr, msg):
        self.file.write('from: {} \n'.format(fromAddr))
        self.file.write('to: {} \n'.format(toAddr))
        self.file.write(msg)
        self.file.write('\n\n')

    def quit(self):
        self.file.close()


class EmailServer:
    """ 
    """
    smtp = None
    responseAddress = ""

    def __init__(self, responseAddress, type, serveraddress="", serverport=587):
        if type == 'smtp':
            smtp = smtplib.SMTP(serveraddress, serverport)
        elif type == 'smtp_ssl':
            server = smtplib.SMTP_SSL(serveraddress, serverport)
        elif type == 'test':
            server = FakeSmtp()
        else:
            raise Exception('Email provider not supported')
        self.responseAddress = responseAddress

    def getLink(self, hash, campaignId):
        return self.responseAddress + "gotphish?s={}&x={}".format(hash, campaignId)

    def send_phish(self, fromAddr, toAddr, toAddrHash, subject, template, campaignId):
        bodyText = Template(template).render(
            link=self.getLink(toAddrHash, campaignId))
        message = MIMEText(bodyText, 'html')
        message['From'] = fromAddr
        message['Subject'] = subject
        message['To'] = toAddr
        msg = message.as_string()
        self.smtp.sendmail(fromAddr, toAddr, msg)

    def __del__(self):
        self.smtp.quit()
