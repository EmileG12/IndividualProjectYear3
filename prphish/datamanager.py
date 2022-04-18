import json

import jinja2
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
from .models import db, EmailResponse, EmailTemplate, Campaign, responseTypes


datamanager = Blueprint('datamanager', __name__)


@datamanager.route("/getresponses")
def selectcampaign():
    prepTable = db.session.query(Campaign, EmailTemplate).join(EmailTemplate)
    return render_template("datamanager.html", campaigns=prepTable)


@datamanager.route("/getresponses", methods=['POST'])
def selectcampaign_post():
    campaignId = request.form.get("campaignid")
    matchemails = request.form.get("matchemails")
    campaign = db.session.query(Campaign, EmailTemplate).filter_by(
        id=campaignId).join(EmailTemplate).join(EmailResponse)
    if "yes" in matchemails:
        emailhashfile = request.form.get("emailhashfile")
        return emailmatching(emailhashfile, campaign)
    responses = {}
    for x in responseTypes:
        r = db.session.query(EmailResponse).filter_by(
            campaignId=campaignId).filter_by(response=x).count()
        responses[x] = r
    return render_template("dataresponse.html", campaign=campaign)


def emailmatching(emailhashfile, campaign):
    emaildictprep = json.loads(emailhashfile)
    hashpairlist = emaildictprep["email_hashedlist"]
    matchcount = 0
    for row in campaign:
        if row.EmailResponse.emailID in hashpairlist.values():
            matchcount = matchcount + 1
    if matchcount == 0:
        flash("No matches found, please try another file")
        return render_template("datamanager.html",
                               campaigns=db.session.query(Campaign, EmailTemplate).join(EmailTemplate))
    elif matchcount < (len(hashdict) / 4):
        flash("Less than 25% of addresses matched, data or file may be outdated")
        return render_template("dataresponse.html", campaign=campaign)
