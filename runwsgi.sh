#!/bin/bash

source venv/bin/activate
export FLASK_APP=prphish
uwsgi --ini wsgi.ini
