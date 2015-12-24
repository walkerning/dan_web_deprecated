#-*- coding: utf-8 -*-
import os
from flask import Flask
app = Flask('hi')
app.config.from_pyfile('dan_web/app_conf.py')
from dan_web.model import init_db
from flask.ext.sqlalchemy import SQLAlchemy
init_db(app)
from dan_web.model import (db, User, Job)

a_conf = {
    'job_type': 'svd_tool',
    'job_name': 'job_2',
    'input_proto': 'try.prototxt',
    'input_caffemodel': 'trytrytry.caffemodel',
    'output_proto': 'try_output.prototxt',
    'output_caffemodel': 'try_output,caffemodel',
    'layer_name': 'fc7',
    'layer_method': 'rank'}

from dan_web.job_runner import JobRunner

os.environ['DAN_WEB_SHARED_DATA_PATH'] = app.config['WRITE_TO_ENV']['DAN_WEB_SHARED_DATA_PATH']
job = Job.get(5)
runner = JobRunner(job,db)
runner.run()

