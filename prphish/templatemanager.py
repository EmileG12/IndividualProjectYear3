import os

import bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
from flask_login import login_required, current_user
from datetime import date, datetime
import uuid
import jinja2
from .models import db, EmailTemplate

templatemanager = Blueprint('templatemanager', __name__)


@templatemanager.route('/templatemanager')
@login_required
def managetemplates():
    templates = EmailTemplate.query.order_by(EmailTemplate.id)
    return render_template('template/templateManager.html', templates=templates)


@templatemanager.route('/addtemplate')
@login_required
def addtemplate():
    return render_template('template/addTemplate.html')


@templatemanager.route('/template')
@login_required
def template():
    cid = request.args.get('id', -1, type=int)
    template = None
    if cid == -1:
        flash('no template')
    else:
        template = EmailTemplate.query.filter_by(id=cid).first()
    return render_template('template/template.html', template=template)


@templatemanager.route('/addtemplate', methods=['POST'])
@login_required
def addtemplate_post():
    templateName = request.form.get('templatename')
    if not templateName:
        flash('Template name is mandatory')
        return redirect(url_for('.addtemplate'))

    emailTemplate = request.files.get('emailTemplate')
    emailCheck = (False,False)
    if not emailTemplate:
        flash('Email body is mandatory')
        return redirect(url_for('.addtemplate'))
    checkEmTemp = jinja2.Environment(loader=jinja2.BaseLoader).from_string(emailTemplate.read().decode("utf-8"))
    checkvar = str(uuid.uuid4())
    checkTemp = checkEmTemp.render(phishlink =checkvar)

    if checkvar in checkTemp:
        emailCheck = True
        emailTemplateHash = bcrypt.hashpw(templateName.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')
    else:
        flash("Email content template does not contain phishlink variable, please edit and add link")
        return redirect(url_for('.addtemplate'))

    responseTemplate = request.files.get("responseTemplate")
    responsename = None
    responseTemplateCheck = (False,False)
    if responseTemplate:
        responseTemplateCheck = (True, False)
        print(responseTemplateCheck)
        try:
            rtemplate = jinja2.Environment(loader=jinja2.BaseLoader).from_string(responseTemplate.read().decode("utf-8"))
            checkStrings = [str(uuid.uuid4()), str(uuid.uuid4())]
            downCheckString = str(uuid.uuid4())
            checkTemp = rtemplate.render(emailId=checkStrings[0], campaignId=checkStrings[1], downloadLink=downCheckString)
        except:
            flash("Response template file cannot be rendered, please edit and reupload")
            return render_template("template/addTemplate.html")
        if (all(x in checkTemp for x in checkStrings) and '<form method="POST" action="/gotphish">' in checkTemp) or downCheckString in checkTemp:
            print(responseTemplateCheck)
            responseTemplateCheck = (True, True)
            responsename= responseTemplate.filename
        else:
            flash("Response template format incorrect, please edit and reupload")
            return redirect(url_for('.addtemplate'))
    else:
        responsename = None
    materialTemplate = request.files.get("materialTemplate")
    materialname = None
    materialTemplateCheck = (False,False)
    if materialTemplate:
        materialTemplateCheck = (True,False)
        materialTemplateCheck = (True, True)
        materialname = materialTemplate.filename
    else:
        materialTemplatePath = None

    saveChecks = [emailCheck,responseTemplateCheck,materialTemplateCheck]
    saveCheck = templateSaveChecker(saveChecks)
    if type(saveCheck) is not str:
        emailTemplateHash = bcrypt.hashpw(templateName.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')
        emailTemplatePath = os.path.join(
            current_app.config['UPLOAD_FOLDER'], emailTemplate.filename)
        emailTemplate.stream.seek(0)
        emailTemplate.save(emailTemplatePath)
        if saveCheck == 1:
            print("blah")
        elif saveCheck == 2:
            responseTemplatePath = os.path.join(
                current_app.config['UPLOAD_FOLDER'], responseTemplate.filename)
            responseTemplate.seek(0)
            responseTemplate.save(responseTemplatePath)
            responsename = responseTemplate.filename
            materialTemplatePath = os.path.join(
                current_app.config['UPLOAD_FOLDER'], materialTemplate.filename)
            materialTemplate.save(materialTemplatePath)
            materialname = materialTemplate.filename
        elif saveCheck == 3:
            responseTemplatePath = os.path.join(
                current_app.config['UPLOAD_FOLDER'], responseTemplate.filename)
            responseTemplate.seek(0)
            responseTemplate.save(responseTemplatePath)
            responsename = responseTemplate.filename
        elif saveCheck == 4:
            materialTemplatePath = os.path.join(
                current_app.config['UPLOAD_FOLDER'], materialTemplate.filename)
            materialTemplate.save(materialTemplatePath)
            materialname = materialTemplate.filename
    else:
        return saveCheck
    newTemplate = EmailTemplate(
        hash=emailTemplateHash, name=templateName, path=emailTemplatePath, responsepagetemplatename=responsename, materialtemplatename=materialname)
    db.session.add(newTemplate)
    db.session.commit()
    return redirect(url_for('.template', id=newTemplate.id))



def templateSaveChecker(saveChecks):
    if saveChecks[0]:
        respCheck = saveChecks[1]
        matCheck = saveChecks[2]
        if respCheck[0] and matCheck[0]:
            if respCheck[1] and matCheck[1]:
                return 2
            elif not respCheck[1]:
                flash("Response template post field or downloadlink variable not found, please edit file")
                return render_template('template/addTemplate.html')
            elif not matCheck[1]:
                flash("Material template rendering error, please edit file and make sure the template is correctly formatted")
                return render_template('template/addTemplate.html')
            else:
                flash("Response template lacking correct fields and rendering error in material template. \n Please edit both files and reupload")
        elif respCheck[0] and not matCheck[0]:
            if respCheck[1]:
                return 3
            else:
                flash("Response template post field or downloadlink variable not found, please edit file")
                return render_template('template/addTemplate.html')
        elif not respCheck[0] and matCheck[0]:
            if matCheck[1]:
                return 4
            else:
                flash(
                    "Material template rendering error, please edit file and make sure the template is correctly formatted")
                return render_template('template/addTemplate.html')
        else:
            return 1
    else:
        return 0