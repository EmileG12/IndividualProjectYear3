import os

import bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
from flask_login import login_required, current_user
from datetime import date, datetime

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
    templateFile = request.files.get('templatefile')
    templateName = request.form.get('templatename')
    templateHash = bcrypt.hashpw(templateName.encode(
        'utf-8'), bcrypt.gensalt()).decode('utf-8')
    custompagechecks = request.form.getlist("custompageargs")
    if "yespost" in custompagechecks:
        postpagetemplate = request.files.get("customresponsepagefile")
        responsepagepath = os.path.join(
            current_app.config['UPLOAD_FOLDER'], postpagetemplate.filename)
        postpagetemplate.save(responsepagepath)
    else:
        responsepagepath = None
    templatePath = os.path.join(
        current_app.config['UPLOAD_FOLDER'], templateFile.filename)
    templateFile.save(templatePath)
    newTemplate = EmailTemplate(
        hash=templateHash, name=templateName, path=templatePath, reponsepagepath=responsepagepath)
    db.session.add(newTemplate)
    db.session.commit()
    return redirect(url_for('.template', id=newTemplate.id))
