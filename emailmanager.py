import smtplib
from email.mime.text import MIMEText
from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db

from flask import Blueprint, render_template, redirect, url_for
import time
emailmanager = Blueprint('emailmanager', __name__)

@emailmanager.route('/manageemails')
def manageemails():
    return render_template('emailmanager.html')

@emailmanager.route('/sendemail')
def sendemail():
    return render_template('sendemail.html')

@emailmanager.route('/sendemail', methods=['POST'])
def sendemail_post():
    sendaddr = request.form.get('sendaddr')
    password = request.form.get('password')
    FakeName = request.form.get('fakename')
    toaddr = request.form.get('toaddr')
    subject = request.form.get('subject')
    contentfile = request.files.get('contentfile')

    msg = MIMEText(contentfile.stream.read().__str__(), 'html')
    msg['From'] = FakeName
    msg['To'] = toaddr
    msg['Subject'] = subject

    if "@gmail" in sendaddr:
        time.sleep(5)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sendaddr, password)
        text = msg.as_string()
        server.sendmail(sendaddr, toaddr, text)
        server.quit()
        flash('Email sent')

    #Functioning email sending
    elif "@hotmail" in sendaddr or "@outlook" in sendaddr or "@live" in sendaddr:
        time.sleep(5)
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sendaddr, password)
        text = msg.as_string()
        server.sendmail(sendaddr, toaddr, text)
        server.quit()
        flash('Email sent')

    elif "@yahoo" in sendaddr:
        print("yahoo")
        time.sleep(5)
        server = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)
        server.starttls()
        server.login(sendaddr, password)
        text = msg.as_string()
        server.sendmail(sendaddr, toaddr, text)
        server.quit()
        flash('Email sent')
    else:
        flash(" Doesn't support that email provider yet")
    return render_template('sendemail.html')