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


@datamanager.route("/responses", methods=['POST'])
def selectcampaign_post():
    if request.files.get('emailhashfile'):
        return emailmatching()
    else:
        return simpleReport()


def simpleReport():
    campaignId = request.form.get("campaignid")
    responses = db.session.query(
        Campaign,
        EmailTemplate,
        EmailResponse.response.label('code'),
        func.count(EmailResponse.response).label('sum')
    ).filter_by(id=campaignId).join(EmailTemplate).join(EmailResponse).group_by(EmailResponse.response)
    types = ResponseTypes.getDict()
    sums = {}
    total = 0
    click = 0
    for row in responses:
        # SENT is a special case, we went to show it at the bottom of the table
        if types[row.code] == 'SENT':
            total = row.sum
        elif types[row.code] == 'CLICK':
            click = row.sum
        else:
            sums[row.code] = row.sum
    # Show 0 if there are no responses of a certain type
    for t in types:
        if not t in sums:
            sums[t] = 0
    print("Campaign ID : " + campaignId)
    return render_template("dataresponse.html",
                           name=responses.first().EmailTemplate.name,
                           datesent=responses.first().Campaign.datesent,
                           types=types,
                           click=click,
                           sums=sums,
                           total=total)


def emailmatching():
    campaignId = request.form.get("campaignid")
    rows = db.session.query(
        Campaign,
        EmailTemplate,
        EmailResponse
    ).filter_by(id=campaignId).join(EmailTemplate).join(EmailResponse)

    # File containing all the email addresses to send the mail to
    try:
        emailFile = request.files.get('emailhashfile')
        emailJson = emailFile.read().decode("utf-8")
        emaildictprep = json.loads(emailJson)
        hashpairlist = emaildictprep["email_hashedlist"]
        # invert key/values
        emailDict = {v: k for k, v in hashpairlist.items()}
    except:
        flash("Invalid email file")
        return redirect(url_for('datamanager.selectcampaign'))

    types = ResponseTypes.getDict()
    # check if the email list is relevant
    matchcount = 0

    # total sent
    total = 0
    click = 0
    sums = {}
    for t in types:
        sums[t] = 0

    # individual responses
    responses = {}
    for row in rows:
        id = row.EmailResponse.emailId
        name = 'N/A'
        if id in emailDict:
            name = emailDict[id]
            matchcount = matchcount + 1
        if ResponseTypes(row.EmailResponse.response) != ResponseTypes.SENT:
            if ResponseTypes(row.EmailResponse.response) == ResponseTypes.CLICK:
                click += 1
            else:
                sums[row.EmailResponse.response] += 1
            if not id in responses:
                responses[id] = {
                    'name': name,
                }
            type = types[row.EmailResponse.response]
            if not type in responses[id]:
                responses[id][type] = 1
            else:
                responses[id][type] += 1
        else:
            total += 1

    for t in types:
        if not t in sums:
            sums[t] = 0

    if matchcount == 0:
        print('not match')
        flash("No matches found, please try another file")
        return redirect(url_for('datamanager.selectcampaign'))

    if matchcount < (len(hashpairlist) / 4):
        flash("Less than 25% of addresses matched, data or file may be outdated")
    return render_template("dataresponse.html",
                           name=rows.first().EmailTemplate.name,
                           datesent=rows.first().Campaign.datesent,
                           types=types,
                           click=click,
                           sums=sums,
                           total=total,
                           responses=responses)
