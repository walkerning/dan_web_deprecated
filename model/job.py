# -*- coding: utf-8 -*-
"""
JOB model"""

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Job(db.Model):
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'))
