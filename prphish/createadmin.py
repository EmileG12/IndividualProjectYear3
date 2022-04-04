#!/usr/bin/env python3

# add a default user admin@localhost/admin

import os

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from . import db, app
from .models import User
app.app_context().push()

email = 'admin@localhost'
user = User.query.filter_by(email=email).first()
if user:
    print('admin already exists')
else:
    new_user = User(email=email, name='admin',
                    password=generate_password_hash('admin', method='sha256'))

    db.session.add(new_user)
    db.session.commit()
