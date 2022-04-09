import smtplib
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from datetime import datetime

from .models import db, EmailResponse


responsemanager = Blueprint('responsemanager', __name__)


@responsemanager.route('/gotphish')
def gotphish():
    emailID = request.args.get('s')
    campaignId = request.args.get('x')
    responseDate = datetime.utcnow()
    response = True
    responseRow = EmailResponse(
        emailID=emailID, campaignId=campaignId, responseDate=responseDate, response=response)
    db.session.add(responseRow)
    db.session.commit()
    return render_template('sendemail.html')

