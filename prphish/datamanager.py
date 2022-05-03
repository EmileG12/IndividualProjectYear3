from cProfile import run
import json

import jinja2
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
from flask_login import login_required, current_user
from .models import db, EmailResponse, EmailTemplate, Campaign, ResponseTypes
from sqlalchemy import func


datamanager = Blueprint('datamanager', __name__)


@datamanager.route("/getresponses")
@login_required
def selectcampaign():
    prepTable = db.session.query(Campaign, EmailTemplate).join(EmailTemplate)
    return render_template("datamanager.html", campaigns=prepTable)


class CampaignResult:
    types = ResponseTypes.getDict()

    def __init__(self, name, datesent):
        self.name = name
        self.datesent = datesent
        self.sums = {}
        self.total = 0
        self.click = 0


@datamanager.route("/responses", methods=['POST'])
@login_required
def selectcampaign_post():
    if request.files.get('emailhashfile'):
        return emailmatching()
    else:
        return simpleReport()


@datamanager.route("/responsesIndividual", methods=['POST'])
@login_required
def selectcampaigncompare_post():
    campaignId = request.form.get("campaignid")
    if not campaignId:
        flash('unknown campaign')
        return redirect(url_for('datamanager.selectcampaign'))
    responses = db.session.query(
        Campaign,
        EmailTemplate,
        EmailResponse.response.label('code'),
        func.count(EmailResponse.response).label('sum')
    ).filter_by(id=campaignId).join(EmailTemplate).join(EmailResponse).group_by(EmailResponse.response)
    result = campaignResult(responses)

    previouscampaignId = request.form.get("previouscampaignid")
    previousresponses = db.session.query(
        Campaign,
        EmailTemplate,
        EmailResponse.response.label('code'),
        func.count(EmailResponse.response).label('sum')
    ).filter_by(id=previouscampaignId).join(EmailTemplate).join(EmailResponse).group_by(EmailResponse.response)
    previousresult = campaignResult(previousresponses)
    return render_template("dataresponse.html",
                           result=result, previousresult=previousresult)


def campaignResult(responses):
    result = CampaignResult(
        responses.first().EmailTemplate.name, responses.first().Campaign.datesent)

    for row in responses:
        # SENT is a special case, we want to show it at the bottom of the table
        if result.types[row.code] == 'SENT':
            result.total = row.sum
        elif result.types[row.code] == 'CLICK':
            result.click = row.sum
        else:
            result.sums[row.code] = row.sum
    # Show 0 if there are no responses of a certain type
    for t in result.types:
        if not t in result.sums:
            result.sums[t] = 0
    return result


def simpleReport():
    campaignId = request.form.get("campaignid")
    if not campaignId:
        flash('unknown campaign')
        return redirect(url_for('datamanager.selectcampaign'))
    responses = db.session.query(
        Campaign,
        EmailTemplate,
        EmailResponse.response.label('code'),
        func.count(EmailResponse.response).label('sum')
    ).filter_by(id=campaignId).join(EmailTemplate).join(EmailResponse).group_by(EmailResponse.response)
    result = campaignResult(responses)
    return render_template("dataresponse.html",
                           result=result)


def emailmatching():
    campaignId = request.form.get("campaignid")
    if not campaignId:
        flash('unknown campaign')
        return redirect(url_for('datamanager.selectcampaign'))
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

    # check if the email list is relevant
    matchcount = 0

    result = CampaignResult(
        rows.first().EmailTemplate.name, rows.first().Campaign.datesent)

    for t in result.types:
        result.sums[t] = 0

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
                result.click += 1
            else:
                result.sums[row.EmailResponse.response] += 1
            if not id in responses:
                responses[id] = {
                    'name': name,
                }
            type = result.types[row.EmailResponse.response]
            if not type in responses[id]:
                responses[id][type] = 1
            else:
                responses[id][type] += 1
        else:
            result.total += 1

    for t in result.types:
        if not t in result.sums:
            result.sums[t] = 0

    if matchcount == 0:
        print('not match')
        flash("No matches found, please try another file")
        return redirect(url_for('datamanager.selectcampaign'))

    if matchcount < (len(hashpairlist) / 4):
        flash("Less than 25% of addresses matched, data or file may be outdated")
    return render_template("dataresponse.html",
                           result=result,
                           responses=responses)
