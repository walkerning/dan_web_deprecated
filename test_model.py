#-*- coding: utf-8 -*-

from flask import Flask
app = Flask('hi')
app.config.from_pyfile('dan_web/app_conf.py')
from dan_web.model import init_db
from flask.ext.sqlalchemy import SQLAlchemy
init_db(app)
from dan_web.model import (db, User, Job)
from dan_web.adapter.secure import secure_conf

from dan_web.job_runner import JobRunner

create_user = User.create_user
