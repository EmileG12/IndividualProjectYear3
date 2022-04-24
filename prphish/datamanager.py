import json

import jinja2
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
from .models import db, EmailResponse, EmailTemplate, Campaign, ResponseTypes
from sqlalchemy import func


datamanager = Blueprint('datamanager', __name__)


@datamanager.route("/getresponses")
def selectcampaign():
    prepTable = db.session.query(Campaign, EmailTemplate).join(EmailTemplate)
    return render_template("datamanager.html", campaigns=prepTable)


@datamanager.route("/getresponses", methods=['POST'])
def selectcampaign_post():
    campaignId = request.form.get("campaignid")
    matchemails = request.form.get("matchemails")
    responses = db.session.query(
        Campaign,
        EmailTemplate,
        EmailResponse.response.label('code'),
        func.count(EmailResponse.response).label('sum')
    ).filter_by(id=campaignId).join(EmailTemplate).join(EmailResponse).group_by(EmailResponse.response)
    # if matchemails:
    #     emailhashfile = request.form.get("emailhashfile")
    #     return emailmatching(emailhashfile, campaign)
    types = ResponseTypes.getDict()
    sums = {}
    total = 0
    #for each type of code, record the sum
    for row in responses:
        #SENT is a special case, we went to show it at the bottom of the table
        if types[row.code] == 'SENT':
            total = row.sum
        else:
            sums[row.code] = row.sum
    #Show 0 if there are no responses of a certain type
    for t in types:
        if not t in sums:
            sums[t] = 0
    print("Campaign ID : " + campaignId)
    return render_template("dataresponse.html",
                           name=responses.first().EmailTemplate.name,
                           datesent=responses.first().Campaign.datesent,
                           types=types,
                           sums=sums,
                           total=total)


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
    elif matchcount < (len(hashpairlist) / 4):
        flash("Less than 25% of addresses matched, data or file may be outdated")
        return render_template("dataresponse.html", campaign=campaign)
