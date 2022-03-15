from flask import Blueprint, render_template, redirect, url_for
from . import db

campaignmanager = Blueprint('campaignmanager', __name__)


@campaignmanager.route('/campaignmanager')
def managecampaigns():
    return render_template('campaignmanager.html')

@campaignmanager.route('/addcampaign')
def addcampaign():
    return render_template('addcampaign.html')

@campaignmanager.route('/retrievecampaign')
def retrievecampaign():
    return render_template('retrievecampaign.html')
