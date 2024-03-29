from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from enum import IntEnum

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
    templatehash = db.Column(db.String(), db.ForeignKey("email_template.hash"))
    emailhashlist = db.Column(db.String())

# Database containing all responses to all campaigns
# response is currently a boolean indicating whether the link was clicked or not


class EmailResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emailId = db.Column(db.String(70))
    campaignId = db.Column(db.String(), db.ForeignKey("campaign.id"))
    responseDate = db.Column(db.DateTime())
    response = db.Column(db.Integer())

# helper function to record a response


def record_response(emailId, campaignId, responseDate, responseCode):
    responseRow = EmailResponse(emailId=emailId, campaignId=campaignId, responseDate=responseDate,
                                response=responseCode)
    db.session.add(responseRow)
    db.session.commit()


# Database containing email templates to be used
# Contains a name for ease of use by users, a path to the email and a hash
# Hash is currently used to recover the file and name, but ID is also used in case it needs to be modified


class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(100))
    name = db.Column(db.String())
    path = db.Column(db.String())
    responsepagetemplatename = db.Column(db.String())
    materialtemplatename = db.Column(db.String())


class ResponseTypes(IntEnum):
    SENT = 0
    CLICK = 1
    POST = 2
    DOWNLOAD = 3

    def getDict():
        d = {}
        for t in ResponseTypes:
            d[int(t)] = t.name
        return d
