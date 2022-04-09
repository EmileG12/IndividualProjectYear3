#!/bin/bash

# use a virtual environment with the required modules

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# create a default user admin@localhost / admin
FLASK_APP=prphish python3 -m prphish.install