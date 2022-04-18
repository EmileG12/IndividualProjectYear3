import smtplib
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
import flask_sqlalchemy
from datetime import datetime
import jinja2
from .models import db, EmailResponse, EmailTemplate, Campaign, responseTypes

responsemanager = Blueprint('responsemanager', __name__)


@responsemanager.route('/gotphish')
def gotphish():
    emailId = request.args.get('s')
    campaignId = request.args.get('x')
    amidownloading = request.args.get('p')
    templateId = Campaign.query.filter_by(id=campaignId).first().templatehash
    responsetemplatename = EmailTemplate.query.filter_by(hash=templateId).first().responsepagetemplatename
    materialtemplatename = EmailTemplate.query.filter_by(hash=templateId).first().materialtemplatename
    if responsetemplatename is not None:
        record_response(emailId,campaignId,datetime.utcnow(),1)
        templateLoader = jinja2.FileSystemLoader(current_app.config['UPLOAD_FOLDER'])
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(responsetemplatename)
        return template.render(emailId=emailId, campaignId=campaignId)
    if amidownloading == 1:
        record_response(emailId, campaignId, datetime.utcnow(), 3)
        return render_template('sendemail.html')
    record_response(emailId,campaignId, datetime.utcnow(), 1)
    return render_template('sendemail.html')


@responsemanager.route('/gotphish', methods=['POST'])
def gotphish_post():
    emailId = request.form.get("s")
    campaignId = request.form.get("x")
    record_response(emailId, campaignId, datetime.utcnow(), 2)
    return render_template("login.html")

def record_response(emailId, campaignId, responseDate, responseCode):
        responseRow = EmailResponse(emailID=emailId, campaignId=campaignId, responseDate=responseDate,
                                    response=responseCode)
        db.session.add(responseRow)
        db.session.commit()


def material_render(materialtemplatename):
    if materialtemplatename is not None:
        templateLoader = jinja2.FileSystemLoader(current_app.config['UPLOAD_FOLDER'])
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(materialtemplatename)
        return template.render()
    else:
        return render_template("login.html")
