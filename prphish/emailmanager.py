import datetime
import smtplib
import uuid
from email.mime.text import MIMEText
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user
from jinja2 import Template
import hashlib
# Bcrypt package install needed
import bcrypt

from flask import Blueprint, render_template, redirect, url_for
import io

from prphish.models import db, EmailTemplate, Campaign

emailmanager = Blueprint('emailmanager', __name__)


@emailmanager.route('/manageemails')
@login_required
def manageemails():
    return render_template('emailmanager.html')


@emailmanager.route('/sendemail')
@login_required
def sendemail():
    templates = EmailTemplate.query.order_by(EmailTemplate.id)
    return render_template('sendemail.html',templates=templates)


def linkmaker(emailID, campaignID):
    phishlink = url_for('responsemanager.gotphish') + "?s=" + emailID + "&x=" + campaignID
    return phishlink


def sendmassmail(sendaddr, password, FakeName, subject, toaddrfile, templatehash, server):
    server.starttls()
    server.login(sendaddr, password)
    hashlist = ""
    # Unique ID for campaign is created
    campaignId = str(uuid.uuid4())
    campaignDatetime = datetime.datetime.utcnow()
    # List of email addresses to send to is hashed without a salt
    # So that we may recover the responses of a specific list of emails later
    hasher = hashlib.sha256()
    hasher.update(toaddrfile.read())
    campaignlisthash = hasher.hexdigest()
    campaign = Campaign(id=campaignId, datesent=campaignDatetime, templatehash=templatehash, emailhashlist=campaignlisthash)
    db.session.add(campaign)
    db.session.commit()
    # Template hash is used to recover file from the database
    templatefile = open(EmailTemplate.query.filter_by(hash=templatehash).first().path, "r")
    msg = templatefile.read()
    # Read file containing addresses to send to as a list
    toaddrlist = toaddrfile.read().decode("utf-8").replace(" ", "").split(",")
    for toaddr in toaddrlist:
        toaddrhash = bcrypt.hashpw(toaddr.encode('utf-8'),bcrypt.gensalt()).decode('utf-8') + " ; "
        hashlist = hashlist + toaddr + " , " + toaddrhash
        templatePrep = Template(msg)
        message = templatePrep.render(link = linkmaker(toaddrhash, campaignId))
        message = MIMEText(message, 'html')
        message['From'] = FakeName
        message['Subject'] = subject
        message['To'] = toaddr
        text = message.as_string()
        server.sendmail(sendaddr, toaddr, text)
    server.quit()
    hashlistbytes = io.BytesIO(bytes(hashlist, "utf-8"))
    return send_file(hashlistbytes)




@emailmanager.route('/sendemail', methods=['POST'])
@login_required
def sendemail_post():
    sendaddr = request.form.get('sendaddr')
    password = request.form.get('password')
    FakeName = request.form.get('fakename')
    subject = request.form.get('subject')
    # File containing the content of the email
    templatehash = request.form.get('templatepath')
    # File containing all the email addresses to send the mail to
    toaddrfile = request.files.get('toaddrfile')

    if "@gmail" in sendaddr:
       server = smtplib.SMTP('smtp.gmail.com', 587)
       sendmassmail(sendaddr, password, FakeName, subject, toaddrfile, templatehash, server)
    elif "@hotmail" in sendaddr or "@outlook" in sendaddr or "@live" in sendaddr:
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        sendmassmail(sendaddr,password, FakeName, subject, toaddrfile, templatehash, server)
    elif "@yahoo" in sendaddr:
        server = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)
        sendmassmail(sendaddr,password, FakeName, subject, toaddrfile, templatehash, server)
    else:
        flash('Email provider not supported')
    return render_template('sendemail.html',)
