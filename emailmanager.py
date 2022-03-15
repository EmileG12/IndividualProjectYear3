from flask import Blueprint, render_template, redirect, url_for
from . import db

emailmanager = Blueprint('emailmanager', __name__)

@emailmanager.route('/manageemails')
def manageemails():
    return render_template('emailmanager.html')

@emailmanager.route('/sendemail')
def sendemail():
    return render_template('sendemail.html')