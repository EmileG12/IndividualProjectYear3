import smtplib
from email.mime.text import MIMEText
from flask import Blueprint, render_template, redirect, url_for, request, flash,send_file
from . import db

#Bcrypt package install needed
import bcrypt

from flask import Blueprint, render_template, redirect, url_for
import time
import io

emailmanager = Blueprint('emailmanager', __name__)

@emailmanager.route('/manageemails')
def manageemails():
    return render_template('emailmanager.html')

@emailmanager.route('/sendemail')
def sendemail():
    return render_template('sendemail.html')

def sendmassmail(sendaddr, password, toaddrlist, msg, server):
    server.starttls()
    server.login(sendaddr, password)
    text = msg.as_string()
    for toaddr in toaddrlist:
        hashlist = hashlist + toaddr + " , " + bcrypt.hashpw(toaddr.encode('utf-8'),
                                                             bcrypt.gensalt()).decode('utf-8') + " ; "
        msg['To'] = toaddr
        server.sendmail(sendaddr, toaddr, text)

    server.quit()

@emailmanager.route('/sendemail', methods=['POST'])
def sendemail_post():
    sendaddr = request.form.get('sendaddr')
    password = request.form.get('password')
    FakeName = request.form.get('fakename')
    subject = request.form.get('subject')
    #File containing the content of the email
    contentfile = request.files.get('contentfile')
    #File containing all the email addresses to send the mail to
    toaddrfile = request.files.get('toaddrfile')

    #Toaddr file is read and split into a list containing all the email addresses
    x = toaddrfile.read().decode("utf-8").replace(" ", "").split(",")

    msg = MIMEText(contentfile.stream.read().decode('UTF8'), 'html')

    msg['From'] = FakeName
    msg['Subject'] = subject
    hashlist = ""

    if "@gmail" in sendaddr:
       # server = smtplib.SMTP('smtp.gmail.com', 587)
        for toaddr in x:
            #Each address is hashed and salted, and a list of all addresses and their hash is created
            #Emails and hashes are separated by a comma, while pairs are separated by a semicolon
            hashlist = hashlist + toaddr + " , " + bcrypt.hashpw(toaddr.encode('utf-8'),
                                                                 bcrypt.gensalt()).decode('utf-8') + " ; "
            flash(toaddr)
        #hashlist is prepared for sending
        hashlistbytes = io.BytesIO(bytes(hashlist, "utf-8"))
        #List of emails and hashes is sent to the client

        return send_file(hashlistbytes, "text/plain", True, "Hashlist.txt")

    elif "@hotmail" in sendaddr or "@outlook" in sendaddr or "@live" in sendaddr:
        #server = smtplib.SMTP('smtp.live.com', 587)
        for toaddr in x:
            hashlist = hashlist + toaddr + " , " + bcrypt.hashpw(toaddr.encode('utf-8'),
                                                                 bcrypt.gensalt()).decode('utf-8') + " ; "
            flash(toaddr)
        hashlistbytes = io.BytesIO(bytes(hashlist, "utf-8"))
        return send_file(hashlistbytes, "text/plain",True, "Hashlist.txt" )
    elif "@yahoo" in sendaddr:
        #server = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)
        for toaddr in x:
            hashlist = hashlist + toaddr + " , " + bcrypt.hashpw(toaddr.encode('utf-8'),
                                                                 bcrypt.gensalt()).decode('utf-8') + " ; "
            flash(toaddr)
        hashlistbytes = io.BytesIO(bytes(hashlist, "utf-8"))
        #sendmassmail(sendaddr,password, x, msg, server)
        return send_file(hashlistbytes, "text/plain",True, "Hashlist.txt")

    else:
        flash('Email provider not supported')
    return render_template('sendemail.html')