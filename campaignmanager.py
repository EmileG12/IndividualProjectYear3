import os

import bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file,current_app

from project.models import Campaign
from . import db
from . import models

campaignmanager = Blueprint('campaignmanager', __name__)


@campaignmanager.route('/campaignmanager')
def managecampaigns():
    return render_template('campaignmanager.html')


@campaignmanager.route('/addcampaign')
def addcampaign():
    return render_template('addcampaign.html')


@campaignmanager.route('/addcampaign', methods=['POST'])
def addcampaign_post():
    campaignfile = request.files.get('campaignfile')
    campaignname = request.form.get('campaignname')
    campaignID = bcrypt.hashpw(campaignname.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if campaignfile.filename == '':
        flash('no file')
    campaignpath = os.path.join(current_app.config['UPLOAD_FOLDER'], campaignfile.filename)
    campaignfile.save(campaignpath)
    campaignRow = Campaign(id=campaignID, campaignName=campaignname, campaignPath=campaignpath)
    db.session.add(campaignRow)
    db.session.commit()
    return render_template('addcampaign.html')


@campaignmanager.route('/retrievecampaign')
def retrievecampaign():
    return render_template('retrievecampaign.html')
