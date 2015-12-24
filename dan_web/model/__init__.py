# -*- coding: utf-8 -*-

import datetime
import os
import shutil
import json
from werkzeug import generate_password_hash, check_password_hash

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin
from dan_web.helper import chdir
from dan_web.adapter.job_adapter import get_adapter

approot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def init_db(app):
    db = SQLAlchemy(app)
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
                new_user.make_dirs()
                return new_user

        # fixme: 做了很多重复的工作, 可以考虑用一个元类啥的实现比较好
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
            # fixme: 这里是不是也可以使用active标志, 不过user删除较少先不改
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

        def get_user_log_dir(self):
            relative_dir_path = os.path.join(app.config['USER_LOG_DIR'], str(self.user_id))
            user_log_dir_path = os.path.join(approot, relative_dir_path)
            return user_log_dir_path

        def get_user_conf_dir(self):
            relative_dir_path = os.path.join(app.config['USER_CONF_DIR'], str(self.user_id))
            user_conf_dir_path = os.path.join(approot, relative_dir_path)
            return user_conf_dir_path

        def get_user_dir(self, dir_name=""):
            relative_dir_path = os.path.join(app.config['UPLOAD_DIR'], str(self.user_id))
            user_dir_path = os.path.join(approot, relative_dir_path)
            return os.path.join(user_dir_path, dir_name)

        def delete_user_file(self, dir_name, file_name):
            # fixme: 是否需要更严格的检查, 外面已经检查过了, 但是这里是不是最好也检查一遍
            os.remove(os.path.join(self.get_user_dir(), dir_name, file_name))

        def make_dirs(self):
            user_dir_path = self.get_user_dir()
            user_conf_dir_path = self.get_user_conf_dir()
            user_log_dir_path = self.get_user_log_dir()

            # shutil.rmtree(user_dir_path, ignore_errors=True)
            # fixme: 怎么把它们弄成一个配置文件, 只能装到working set吗
            os.mkdir(user_dir_path)
            os.mkdir(user_conf_dir_path)
            os.mkdir(user_log_dir_path)
            # for test
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

        def get_running_jobs(self):
            return Job.query.filter_by(active=True, user_id=self.user_id, job_status='running').all()


    class Job(db.Model):
        __tablename__ = 'JOB'

        job_id = db.Column(db.Integer, primary_key = True, nullable=False,
                           autoincrement=True)
        job_name = db.Column(db.String(30), nullable=False)
        job_type = db.Column(db.String(20), nullable=False)
        job_conf = db.Column(db.String(50))
        job_status = db.Column(db.String(10), nullable=False) # starting, running, failed, success
        log_file = db.Column(db.String(50))
        log_deleted = db.Column(db.BOOLEAN, db.ColumnDefault(False))
        active = db.Column(db.BOOLEAN, db.ColumnDefault(True))
        create_time = db.Column(db.DATETIME, db.ColumnDefault(datetime.datetime.utcnow()))
        end_time = db.Column(db.DATETIME)
        running_pid = db.Column(db.Integer)
        user_id = db.Column('user_id', db.Integer, db.ForeignKey('USER.user_id'), nullable=False)

        def __init__(self, user_id, job_name, job_type):
            self.user_id = user_id
            self.job_name = job_name
            self.job_type = job_type
            self.job_status = "starting"

        @classmethod
        def create_job(cls, user_id, conf):
            """
            conf: 包含所有配置的dict, 先要检查配置是否完全"""
            if not "job_name" in conf or not "job_type" in conf:
                # 必要的配置没有提供
                return None
            adapter =  get_adapter([('job_type', conf["job_type"])])

            if adapter is None:
                # 无效的job_type
                return None
            if not set(adapter.required.keys()) < set(conf.keys()):
                # fixme:还没想好optional怎么处理, 先不管
                # 必要的配置没有提供
                return None
            valid_conf_name_set = set(adapter.required.keys()).union(set(adapter.optional.keys()))
            conf_obj = {key:value for key,value in conf.iteritems()
                        if key in valid_conf_name_set}

            # fixme: 没给job_conf加随机数, 因为job_id暂时是唯一的
            new_job = cls(user_id, conf["job_name"], conf["job_type"])
            try:
                db.session.add(new_job)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print e
                return None
            else:
            # 写入conf文件
                new_job.job_conf = str(new_job.job_id) + '_conf.json'
                json.dump(conf_obj, open(os.path.join(User.get(user_id).get_user_conf_dir(),
                                                  new_job.job_conf), 'w'))

                # 生成log file 暂时也没有给log file加随机数
                # fixme: 先使用一个独立的文件夹了, 如果要用tmpdir以后再说
                new_job.log_file = str(new_job.job_id) + '.log'
                try:
                    db.session.add(new_job)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print e
                    return None
                return new_job


        def get_id(self):
            """
            for sqlachelmy"""
            return unicode(self.job_id)

        def get_conf(self):
            # 读配置文件并返回配置dict
            # fixme: 错误处理是在这里做还是在外面catch这里要统一. 感觉在这里做比较较好. 那这样的话如果失败需要一个error_string.
            return json.load(open(self.abs_conf_file, 'r'))

        def get_abs_data_file(self, data_file_path):
            return os.path.join(User.get(self.user_id).get_user_dir(),
                                data_file_path)

        @property
        def abs_log_file(self):
            return os.path.join(User.get(self.user_id).get_user_log_dir(),
                                self.log_file)

        @property
        def abs_conf_file(self):
            return os.path.join(User.get(self.user_id).get_user_conf_dir(),
                                self.job_conf)

        @classmethod
        def get_job_list_by_user_id(cls, user_id):
            return cls.query.filter_by(user_id=user_id, active=True).all()

        @classmethod
        def get(cls, job_id):
            return cls.query.filter_by(job_id=int(job_id), active=True).first()

        @classmethod
        def get_job_of_user_id(cls, job_id, user_id):
            job = cls.get(job_id)
            if job.user_id == user_id:
                return job
            else:
                # this job is not of this user
                return None

        @classmethod
        def delete_by_job_id(cls, job_id):
            job = cls.get(job_id)
            job.active = False
            db.session.add(job)
            db.session.commit()


    globals().update({
        'db': db,
        'User': User,
        'Job': Job
    })
