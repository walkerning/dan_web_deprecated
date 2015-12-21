# -*- coding: utf-8 -*-
import datetime
import os
import shutil
from werkzeug import generate_password_hash, check_password_hash

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin
from helper import chdir

approot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def init_db(app):
    db = SQLAlchemy(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/dan_test'
    class User(db.Model, UserMixin):
        __tablename__ = 'USER'

        user_id = db.Column(db.Integer, primary_key = True, nullable=False,
                            autoincrement=True)
        user_name = db.Column(db.String(30), unique=True, nullable=False)
        password = db.Column(db.String(66), nullable=False)
        exist_job_limit = db.Column(db.Integer, db.ColumnDefault(5))
        running_job_limit = db.Column(db.Integer, db.ColumnDefault(3))
        create_time = db.Column(db.DATETIME, db.ColumnDefault(datetime.datetime.utcnow()))
        history_job_num = db.Column(db.Integer, db.ColumnDefault(0))
        history_success_job_num = db.Column(db.Integer, db.ColumnDefault(0))

        def __init__(self, user_name, password):
            self.user_name = user_name
            self.set_password(password)

        @classmethod
        def create_user(cls, user_name, password):
            """
            用于创建新用户, 现在不开放注册功能
            由管理员手动创建"""
            new_user = User(user_name, password)
            try:
                db.session.add(new_user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print e
                return None
            else:
                # 新建文件夹
                new_user.make_user_dir()
                return new_user

        @classmethod
        def get(cls, user_id):
            # 用user_id构建一个User并返回
            return User.query.filter_by(user_id=int(user_id)).first()

        @classmethod
        def get_by_user_name(cls, user_name):
            return User.query.filter_by(user_name=user_name).first()

        @classmethod
        def delete_by_user_id(cls, user_id):
            cls.query.filter_by(user_id=int(user_id)).delete()
            db.session.commit()

        @classmethod
        def delete_by_user_name(cls, user_name):
            user = cls.query.filter_by(user_name=user_name)
            user.first().delete_user_dir()
            user.delete()
            db.session.commit()

        @classmethod
        def validate_and_get(cls, user_name, password):
            # validate login user_name and password
            # if the pair is validate, return the User
            ins = cls.get_by_user_name(user_name)
            if ins is None:
                # 无该用户存在
                return None
            elif ins.check_password(password):
                return ins
            else:
                return None

        def get_id(self):
            return unicode(self.user_id)

        def set_password(self, password):
            self.password = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password, password)

        def delete_user_dir(self):
            user_dir_path = self.get_user_dir()
            shutil.rmtree(user_dir_path, ignore_errors=True)

        def get_user_dir(self, dir_name="."):
            relative_dir_path = os.path.join(app.config['UPLOAD_DIR'], str(self.user_id))
            user_dir_path = os.path.join(approot, relative_dir_path)
            return os.path.join(user_dir_path, dir_name)

        def delete_user_file(self, dir_name, file_name):
            # fixme: 是否需要更严格的检查, 外面已经检查过了, 但是这里是不是最好也检查一遍
            os.remove(os.path.join(self.get_user_dir(), dir_name, file_name))

        def make_user_dir(self):
            user_dir_path = self.get_user_dir()
            shutil.rmtree(user_dir_path, ignore_errors=True)
            # fixme: 怎么把它们弄成一个配置文件, 只能装到working set吗
            os.mkdir(user_dir_path)
            import pdb
            pdb.set_trace()
            with chdir(user_dir_path):
                for _dir in ['upload_prototxt', 'upload_caffemodel',
                             'generated_prototxt', 'generated_caffemodel']:
                    try:
                        os.mkdir(_dir)
                    except Exception as e:
                        print e

        def get_file_name_list(self, dir_name):
            relative_dir_path = os.path.join(app.config['UPLOAD_DIR'], str(self.user_id))
            dir_path = os.path.join(approot, relative_dir_path, dir_name)
            if not os.path.isdir(dir_path):
                return []
            else:
                return os.listdir(dir_path)


    class Job(db.Model):
        __tablename__ = 'JOB'

        job_id = db.Column(db.Integer, primary_key = True, nullable=False,
                           autoincrement=True)
        job_name = db.Column(db.String(30), nullable=False)
        job_type = db.Column(db.String(20), nullable=False)
        job_conf = db.Column(db.String(50), nullable=False)
        job_status = db.Column(db.String(10), nullable=False)
        log_file = db.Column(db.String(50), nullable=False)
        log_deleted = db.Column(db.BOOLEAN, db.ColumnDefault(False))
        create_time = db.Column(db.DATETIME, db.ColumnDefault(datetime.datetime.utcnow()))
        end_time = db.Column(db.DATETIME)
        running_pid = db.Column(db.Integer)
        user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'))

    globals().update({
        'db': db,
        'User': User,
        'Job': Job
    })
