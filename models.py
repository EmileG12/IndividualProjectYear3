from . import db
from flask_login import UserMixin

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class EmailResponse(db.Model):
    emailID = db.Column(db.String(70), primary_key=True)
    campaignID = db.Column(db.String(70), primary_key=True)
    responseDate = db.Column(db.DateTime())
    response = db.Column(db.Boolean())

class Campaign(db.Model):
    id = db.Column (db.String(100), primary_key=True)
    campaignName = db.Column(db.String(100))
    campaignPath = db.Column(db.String(100))

