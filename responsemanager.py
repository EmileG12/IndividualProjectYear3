import datetime
import smtplib
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file

from project.models import EmailResponse
from . import db


responsemanager = Blueprint('responsemanager', __name__)


@responsemanager.route('/gotphish')
def gotphish():
    emailID = request.args.get('s')
    campaignID = request.args.get('x')
    responseDate = datetime.datetime.utcnow()
    response = True
    responseRow = EmailResponse(emailID=emailID, campaignID=campaignID, responseDate=responseDate,response=response)
    db.session.add(responseRow)
    db.session.commit()
    flash("CampaignID: " + campaignID + "EmailID: " + emailID )
    return render_template('sendemail.html')

@responsemanager.route('/gotphish', methods=['GET'])
def gotphish_get():
    emailID = request.args.get('s')
    campaignID = request.args.get('x')
    response = True
    responseRow = EmailResponse(emailID=emailID, campaignID=campaignID,response=response)
    db.session.add(responseRow)
    db.session.commit()
    flash("CampaignID: ")
    return render_template('sendemail.html')



