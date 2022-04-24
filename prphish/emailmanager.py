import smtplib

from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user

import datetime
import uuid
import hashlib
# Bcrypt package install needed
import bcrypt
import json

from flask import Blueprint, render_template, redirect, url_for
import io

from .models import db, EmailTemplate, Campaign
from .emailserver import EmailServer

emailmanager = Blueprint('emailmanager', __name__)


@emailmanager.route('/manageemails')
@login_required
def manageemails():
    return render_template('emailmanager.html')


@emailmanager.route('/sendemail')
@login_required
def sendemail():
    templates = EmailTemplate.query.order_by(EmailTemplate.id)
    return render_template('sendemail.html', templates=templates)


@emailmanager.route('/sendemail', methods=['POST'])
@login_required
def sendemail_post():
    # smtp server parameters
    serverType = request.form.get('serverType')
    serverAddress = request.form.get('serverAddress')
    serverPort = request.form.get('serverPort')
    serverUsername = request.form.get('serverUsername')
    serverPassword = request.form.get('serverPassword')
    server = None
    try:
        server = EmailServer(request.host_url, serverType, serverAddress, serverPort,
                             serverUsername, serverPassword)
    except:
        flash('invalid smtp parameters')
        return redirect(url_for('emailmanager.sendemail'))

    # paramter of the phishing email
    sender = request.form.get('sender')
    subject = request.form.get('subject')

    # File containing all the email addresses to send the mail to
    recipientsFile = request.files.get('recipientsFile')

    if not sender or not subject or not recipientsFile:
        flash('Please fill all the mandatory information')
        return redirect(url_for('emailmanager.sendemail'))

    recipients = recipientsFile.read()

    # File containing the content of the email
    templateHash = request.form.get('templateHash')
    # Template hash is used to recover file from the database
    msg = None
    try:
        templatefile = open(EmailTemplate.query.filter_by(
            hash=templateHash).first().path, "r")
        msg = templatefile.read()
    except:
        flash('Invalid Template')
        return redirect(url_for('emailmanager.sendemail'))
    return sendmassmail(sender, subject, recipients, templateHash, msg, server)


def sendmassmail(sender, subject, recipients, templateHash, msg, server):
    # Unique ID for campaign is created
    campaignId = str(uuid.uuid4())
    campaignDatetime = datetime.datetime.utcnow()

    #  List of email addresses to send to is hashed without a salt
    #  So that we may recover the responses based on  a specific list of emails later
    hasher = hashlib.sha256()
    hasher.update(recipients)
    campaignlisthash = hasher.hexdigest()
    campaign = Campaign(id=campaignId, datesent=campaignDatetime,
                        templatehash=templateHash, emailhashlist=campaignlisthash)
    db.session.add(campaign)
    db.session.commit()

    # Read file containing addresses to send to as a list
    toaddrstring = recipients.decode("utf-8")
    print(toaddrstring)
    try:
        prepdict = json.loads(toaddrstring)
    except:
        flash("Email list is not in JSON format, please edit and try again")
        return redirect(url_for('emailmanager.sendemail'))

    if not "email_hashedlist" in prepdict:
        prepdict["email_hashedlist"] = {}

    listchecks = [False,False]
    # calculate hash for new emails and add them to the previous ones
    if "new_emails" in prepdict:
        listchecks[0] = True
        tomailsnew = prepdict["new_emails"]
        for toaddr in tomailsnew:
            toaddrhash = bcrypt.hashpw(toaddr.encode(
                'utf-8'), bcrypt.gensalt()).decode('utf-8')
            prepdict["email_hashedlist"][toaddr] = toaddrhash
        prepdict.pop("new_emails")

    if "email_hashedlist" in prepdict:
        listchecks[1] = True
        tomailshashed = prepdict["email_hashedlist"]
        # send the emails
        recipientRefused = False
        refusedAddresses = []
        for toaddr in tomailshashed:
            toaddrhash = tomailshashed[toaddr]
            try:
                server.send_phish(sender, toaddr, subject, msg, toaddrhash,campaignId)
            except smtplib.SMTPSenderRefused:
                flash("Sender address refused to send email, please fix the issue and try again")
                return redirect(url_for('emailmanager.sendemail'))
            except smtplib.SMTPRecipientsRefused:
                recipientRefused = True
                refusedAddresses = refusedAddresses.append(toaddr)
                continue
            except smtplib.SMTPServerDisconnected:
                flash("SMTP server disconnected, please try again")
                return redirect(url_for('emailmanager.sendemail'))
        if recipientRefused:
            print("System was not able to send to these addresses: " + refusedAddresses + "\n Emails were sent to the rest, please try again" )

        hasher = hashlib.sha256()
        hasher.update(recipients)
        campaignlisthash = hasher.hexdigest()
        campaign = Campaign(id=campaignId, datesent=campaignDatetime,
                            templatehash=templateHash, emailhashlist=campaignlisthash)
        db.session.add(campaign)
        db.session.commit()
        jsonstring = json.dumps(prepdict)
        jsonbytes = io.BytesIO(bytes(jsonstring, "utf-8"))
        return send_file(path_or_file=jsonbytes, mimetype="text/plain", as_attachment=True,
                         attachment_filename="hashlistatt.txt")
    if (not list[0]) and (not list[1]):
        flash("new_emails or email_hashedlist not found, please edit email list and try again")
        return redirect(url_for('emailmanager.sendemail'))

    # error
    flash('No recipients email found')
    return redirect(url_for('emailmanager.sendemail'))
