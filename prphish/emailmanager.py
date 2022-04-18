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
    # templates = EmailTemplate.query.order_by(EmailTemplate.id)
    # return render_template('sendemail.html', templates=templates)
    return render_template("testtemplate.html")


def linkmaker(emailID, campaignID):
    #phishlink = url_for('responsemanager.gotphish') + "?s=" + emailID + "&x=" + campaignID
    phishlink = "http://localhost:5000/" + "gotphish" + \
        "?s=" + emailID + "&x=" + campaignID
    return phishlink

def sendmassmail(sendaddr, password, FakeName, subject, toaddrfile, templatehash, server):
    # server.starttls()
    #server.login(sendaddr, password)
    hashlist = ""
    # Unique ID for campaign is created
    campaignId = str(uuid.uuid4())
    campaignDatetime = datetime.datetime.utcnow()
    # # List of email addresses to send to is hashed without a salt
    # # So that we may recover the responses of a specific list of emails later
    hasher = hashlib.sha256()
    hasher.update(toaddrfile)
    campaignlisthash = hasher.hexdigest()
    campaign = Campaign(id=campaignId, datesent=campaignDatetime,
                        templatehash=templatehash, emailhashlist=campaignlisthash)
    db.session.add(campaign)
    db.session.commit()
    # Template hash is used to recover file from the database
    templatefile = open(EmailTemplate.query.filter_by(
        hash=templatehash).first().path, "r")
    msg = templatefile.read()
    # Read file containing addresses to send to as a list
    toaddrstring = toaddrfile.decode("utf-8")
    prepdict = json.loads(toaddrstring)
    if "email_hashedlist" in prepdict:
        tomailshashed = prepdict["email_hashedlist"]
        for toaddr in tomailshashed:
            toaddrhash = tomailshashed[toaddr]
            send_phishmail(server, msg, toaddr, toaddrhash,
                           campaignId, FakeName, subject, sendaddr)
        flash("Emails sent, no new addresses detected")
        return render_template("sendemail.html", templates=EmailTemplate.query.order_by(EmailTemplate.id))

    if "new_emails" in prepdict:
        tomailsnew = prepdict["new_emails"]
        topairlist = []
        for toaddr in tomailsnew:
            toaddrhash = bcrypt.hashpw(toaddr.encode(
                'utf-8'), bcrypt.gensalt()).decode('utf-8')
            toaddrpair = {toaddr: toaddrhash}
            topairlist.append(toaddrpair)
            send_phishmail(server, msg, toaddr, toaddrhash,
                           campaignId, FakeName, subject, sendaddr)
        if "email_hashedlist" in prepdict:
            tomailshashed = prepdict["email_hashedlist"]
            for toaddr in tomailshashed:
                toaddr = toaddrpair["address"]
                toaddrhash = toaddrpair["hash"]
                send_phishmail(server, msg, toaddr, toaddrhash,
                               campaignId, FakeName, subject, sendaddr)
            newhashdict = tomailshashed + topairlist
            prepdict["email_hashedlist"] = newhashdict
            prepdict["new_emails"] = []
            jsonstring = json.dumps(prepdict)
            jsonbytes = io.BytesIO(bytes(jsonstring, "utf-8"))
            flash("Emails sent and hash pairs added, keep the file you've received securely in order to retrieve data about specific addresses later")
            return send_file(path_or_file=jsonbytes, mimetype="text/plain", as_attachment=True,
                             attachment_filename="hashlistatt.txt")
        else:
            prepdict["email_hashedlist"] = topairlist
            prepdict["new_emails"] = []
            jsonstring = json.dumps(prepdict)
            jsonbytes = io.BytesIO(bytes(jsonstring, "utf-8"))
            flash(
                "Emails sent, keep the file you've received securely in order to retrieve data about specific addresses later")
            return send_file(path_or_file=jsonbytes, mimetype="text/plain", as_attachment=True,
                             attachment_filename="hashlistatt.txt")


def send_phishmail(server, template, toAddr, toAddrHash, campaignId, fromAddr, subject, sendaddr):
    server.send_phish(fromAddr, toAddr, toAddrHash,
                      subject, template, campaignId)
    # templatePrep = Template(msg)
    # message = templatePrep.render(link=linkmaker(toaddrhash, campaignId))
    # message = MIMEText(message, 'html')
    # message['From'] = FakeName
    # message['Subject'] = subject
    # message['To'] = toaddr
    # text = message.as_string()
    # server.sendmail(sendaddr, toaddr, text)


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
    toaddrfile = request.files.get('toaddrfile').read()
    # server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server = EmailServer(request.host_url, type='test')
    return sendmassmail(sendaddr, password, FakeName, subject, toaddrfile, templatehash, server)
    # if "@gmail" in sendaddr:
    #    server = smtplib.SMTP('smtp.gmail.com', 587)
    #    sendmassmail(sendaddr, password, FakeName, subject, toaddrfile, templatehash, server)
    # elif "@hotmail" in sendaddr or "@outlook" in sendaddr or "@live" in sendaddr:
    #     server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    #     sendmassmail(sendaddr,password, FakeName, subject, toaddrfile, templatehash, server)
    # elif "@yahoo" in sendaddr:
    #     server = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)
    #     sendmassmail(sendaddr,password, FakeName, subject, toaddrfile, templatehash, server)
    # else:
    #     flash('Email provider not supported')
    # templates = EmailTemplate.query.order_by(EmailTemplate.id)
    # return render_template('sendemail.html', templates=templates)
