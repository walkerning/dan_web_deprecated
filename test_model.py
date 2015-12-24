#-*- coding: utf-8 -*-

from flask import Flask
app = Flask('hi')
app.config.from_pyfile('dan_web/app_conf.py')
from dan_web.model import init_db
from flask.ext.sqlalchemy import SQLAlchemy
init_db(app)
from dan_web.model import (db, User, Job)
from dan_web.adapter.secure import secure_conf

a_conf = {
    'job_type': 'svd_tool',
    'job_name': 'job_1',
    'input_proto': 'try.prototxt',
    'input_caffemodel': 'trytrytry.caffemodel',
    'output_proto': 'try_output.prototxt',
    'output_caffemodel': 'try_output,caffemodel',
    'layer_name': 'fc7',
    'layer_method': 'rank'}

b_conf = {
    'job_type': 'svd_tool',
    'job_name': 'job_correct',
    'input_proto': 'shared/VGG16ORI.prototxt',
    'input_caffemodel': 'shared/VGG16ORI.caffemodel',
    'output_proto': 'try_output1.prototxt',
    'output_caffemodel': 'try_output1.caffemodel',
    'layer_name': 'fc7',
    'layer_method': 'rank'}

from dan_web.job_runner import JobRunner
