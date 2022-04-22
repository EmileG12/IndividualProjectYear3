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
    print(amidownloading)
    templateId = Campaign.query.filter_by(id=campaignId).first().templatehash
    responsetemplatename = EmailTemplate.query.filter_by(hash=templateId).first().responsepagetemplatename
    materialtemplatename = EmailTemplate.query.filter_by(hash=templateId).first().materialtemplatename
    if responsetemplatename is not None:
        record_response(emailId,campaignId,datetime.utcnow(),1)
        downloadLink = request.host_url + "gotphish?s={}&x={}&p=1".format(emailId, campaignId) + '"'
        templateLoader = jinja2.FileSystemLoader(current_app.config['UPLOAD_FOLDER'])
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(responsetemplatename)
        return template.render(emailId=emailId, campaignId=campaignId,downloadLink=downloadLink)
    if amidownloading == 1:
        record_response(emailId, campaignId, datetime.utcnow(), 3)
        return material_render(materialtemplatename)
    record_response(emailId,campaignId, datetime.utcnow(), 1)
    return material_render(materialtemplatename)

def material_render(materialtemplatename):
    if materialtemplatename is not None:
        templateLoader = jinja2.FileSystemLoader(current_app.config['UPLOAD_FOLDER'])
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(materialtemplatename)
        return template.render()
    else:
        render_template("sendemail.html")


@responsemanager.route('/gotphish', methods=['POST'])
def gotphish_post():
    emailId = request.form.get("emailId")
    campaignId = request.form.get("campaignId")
    print(campaignId)
    templateId = Campaign.query.filter_by(id=campaignId).first().templatehash
    materialtemplatename = EmailTemplate.query.filter_by(hash=templateId).first().materialtemplatename
    print(materialtemplatename)
    record_response(emailId, campaignId, datetime.utcnow(), 2)
    return material_render(materialtemplatename)

def record_response(emailId, campaignId, responseDate, responseCode):
        responseRow = EmailResponse(emailId=emailId, campaignId=campaignId, responseDate=responseDate,
                                    response=responseCode)
        db.session.add(responseRow)
        db.session.commit()

@responsemanager.route('/gotdownload', methods =['GET'])
def download_phish_get():
    emailId= request.args.get('s')
    campaignId = request.args.get('x')
    templateId = Campaign.query.filter_by(id=campaignId).first().templatehash
    materialtemplatename = EmailTemplate.query.filter_by(hash=templateId).first().materialtemplatename
    record_response(emailId,campaignId,datetime.utcnow(), 3)
    return material_render(materialtemplatename)

def material_render(materialtemplatename):
    if materialtemplatename is not None:
        templateLoader = jinja2.FileSystemLoader(current_app.config['UPLOAD_FOLDER'])
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(materialtemplatename)
        return template.render()
    else:
        return render_template("login.html")
