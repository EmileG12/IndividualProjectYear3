#!/bin/bash


source venv/bin/activate
FLASK_APP=prphish python3 -m tests.populate_db
