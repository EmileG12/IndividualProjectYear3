from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# User database used for authentication
class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# Campaign database
# Contains the date the campaign was sent out, a unique ID, the hash of the template used
# and a hash of the list of email addresses used
class Campaign(db.Model):
    id = db.Column(db.String(70), primary_key=True)
    datesent = db.Column(db.DateTime())
    templatehash = db.Column(db.String(100))
    emailhashlist = db.Column(db.String())

# Database containing all responses to all campaigns
# response is currently a boolean indicating whether the link was clicked or not
class EmailResponse(db.Model):
    emailID = db.Column(db.String(70), primary_key=True)
    campaignId = db.Column(db.String(100), primary_key=True)
    responseDate = db.Column(db.DateTime())
    response = db.Column(db.Boolean())

# Database containing email templates to be used
# Contains a name for ease of use by users, a path to the email and a hash
# Hash is currently used to recover the file and name, but ID is also used in case it needs to be modified
class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(100))
    name = db.Column(db.String())
    path = db.Column(db.String(100))
