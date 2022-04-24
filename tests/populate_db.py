#!/usr/bin/env python3

# add a default user admin@localhost/admin

import email
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from prphish import create_app
from prphish.models import ResponseTypes, db, EmailTemplate, Campaign, EmailResponse, ResponseTypes
import datetime
import uuid


app = create_app()
app.app_context().push()

template = EmailTemplate(
    hash='xxxxxx',
    name='test1',
    path='path/to/template',
    responsepagetemplatename='path/to/reponse',
    materialtemplatename='/path/to/material')

db.session.add(template)

campaign = Campaign(
    id=str(uuid.uuid4()),
    datesent=datetime.datetime.utcnow(),
    templatehash=template.hash,
    emailhashlist='hhhh')
db.session.add(campaign)

print(campaign.id)

# create 100 sent email
responses = []
for i in range(0, 100):
    response = EmailResponse(
        emailId=str(uuid.uuid4()),
        campaignId=campaign.id,
        responseDate=datetime.datetime.utcnow(),
        response=int(ResponseTypes.SENT))
    db.session.add(response)
    responses.append(response)

for i in range(0, 30):
    response = EmailResponse(
        id=responses[i].id,
        campaignId=campaign.id,
        responseDate=datetime.datetime.utcnow(),
        response=int(ResponseTypes.CLICK))
    db.session.add(response)

for i in range(20, 40):
    response = EmailResponse(
        emailId=responses[i].emailId,
        campaignId=campaign.id,
        responseDate=datetime.datetime.utcnow(),
        response=int(ResponseTypes.POST))
    db.session.add(response)


for i in range(35, 45):
    response = EmailResponse(
        emailId=responses[i].emailId,
        campaignId=campaign.id,
        responseDate=datetime.datetime.utcnow(),
        response=int(ResponseTypes.DOWNLOAD))
    db.session.add(response)

for i in range(42, 45):
    response = EmailResponse(
        emailId=responses[i].emailId,
        campaignId=campaign.id,
        responseDate=datetime.datetime.utcnow(),
        response=int(ResponseTypes.CLICK))
    db.session.add(response)

for i in range(39, 40):
    response = EmailResponse(
        emailId=responses[i].emailId,
        campaignId=campaign.id,
        responseDate=datetime.datetime.utcnow(),
        response=int(ResponseTypes.CLICK))
    db.session.add(response)

db.session.commit()
