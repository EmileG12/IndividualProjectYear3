import smtplib
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
import flask_sqlalchemy
from datetime import datetime
import jinja2
from .models import db, EmailResponse, EmailTemplate, Campaign, ResponseTypes, record_response
from jinja2 import Template

responsemanager = Blueprint('responsemanager', __name__)


@responsemanager.route('/previewmail')
def previewmail():
    templateId = request.args.get('id')
    templatefile = open(EmailTemplate.query.filter_by(
        id=templateId).first().path, "r")
    return Template(templatefile.read()).render()


@responsemanager.route('/previewphish')
def previewphish():
    templateId = request.args.get('id')
    responsepagetemplatename = EmailTemplate.query.filter_by(
        id=templateId).first().responsepagetemplatename
    return material_render(responsepagetemplatename)


@responsemanager.route('/previewmaterial')
def previewmaterial():
    templateId = request.args.get('id')
    materialtemplatename = EmailTemplate.query.filter_by(
        id=templateId).first().materialtemplatename
    return material_render(materialtemplatename)


@ responsemanager.route('/gotphish')
def gotphish():
    emailId = request.args.get('s')
    campaignId = request.args.get('x')
    templateId = Campaign.query.filter_by(id=campaignId).first().templatehash
    responsetemplatename = EmailTemplate.query.filter_by(
        hash=templateId).first().responsepagetemplatename
    materialtemplatename = EmailTemplate.query.filter_by(
        hash=templateId).first().materialtemplatename
    if responsetemplatename is not None:
        record_response(emailId, campaignId,
                        datetime.utcnow(), ResponseTypes.CLICK)
        downloadLink = request.host_url + \
            "gotdownload?s={}&x={}".format(emailId, campaignId) + '"'
        templateLoader = jinja2.FileSystemLoader(
            current_app.config['UPLOAD_FOLDER'])
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(responsetemplatename)
        return template.render(emailId=emailId, campaignId=campaignId, downloadLink=downloadLink)
    record_response(emailId, campaignId,
                    datetime.utcnow(), ResponseTypes.CLICK)
    return material_render(materialtemplatename)


@ responsemanager.route("/gotdownload")
def gotdownload():
    emailId = request.args.get('s')
    campaignId = request.args.get('x')
    templateId = Campaign.query.filter_by(id=campaignId).first().templatehash
    materialtemplatename = EmailTemplate.query.filter_by(
        hash=templateId).first().materialtemplatename
    record_response(emailId, campaignId, datetime.utcnow(),
                    ResponseTypes.DOWNLOAD)
    return material_render(materialtemplatename)


def material_render(materialtemplatename):
    if materialtemplatename is not None:
        templateLoader = jinja2.FileSystemLoader(
            current_app.config['UPLOAD_FOLDER'])
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(materialtemplatename)
        return template.render()
    else:
        render_template("sendemail.html")


@ responsemanager.route('/gotphish', methods=['POST'])
def gotphish_post():
    emailId = request.form.get("emailId")
    campaignId = request.form.get("campaignId")
    print(campaignId)
    templateId = Campaign.query.filter_by(id=campaignId).first().templatehash
    materialtemplatename = EmailTemplate.query.filter_by(
        hash=templateId).first().materialtemplatename
    print(materialtemplatename)
    record_response(emailId, campaignId, datetime.utcnow(), ResponseTypes.POST)
    return material_render(materialtemplatename)


@ responsemanager.route('/gotdownload', methods=['GET'])
def download_phish_get():
    emailId = request.args.get('s')
    campaignId = request.args.get('x')
    templateId = Campaign.query.filter_by(id=campaignId).first().templatehash
    materialtemplatename = EmailTemplate.query.filter_by(
        hash=templateId).first().materialtemplatename
    record_response(emailId, campaignId, datetime.utcnow(),
                    ResponseTypes.DOWNLOAD)
    return material_render(materialtemplatename)


def material_render(materialtemplatename):
    if materialtemplatename is not None:
        templateLoader = jinja2.FileSystemLoader(
            current_app.config['UPLOAD_FOLDER'])
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(materialtemplatename)
        return template.render()
    else:
        return render_template("login.html")
