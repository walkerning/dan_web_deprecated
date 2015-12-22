# -*- coding: utf-8 -*-

import os

import flask as _f
from dan_web.model import (User, Job)
from flask.ext import login as _l

here = os.path.dirname(os.path.abspath(__file__))
app_root = os.path.dirname(here)

job_blueprint = _f.Blueprint('job', __name__)

@job_blueprint.route('/view/<job_id>', methods=["GET"])
@_l.login_required
def job_item(job_id):
    """
    展示已有的Job的页面"""
    job_list = [(x.job_name, x.job_id) for x in Job.get_job_list_by_user_id(_l.current_user.user_id)]
    # 确认是否该job_id为该user的
    job = Job.get_job_of_user_id(job_id, _l.current_user.user_id)
    if job is None:
        return _f.abort(404)
    else:
        return _f.render_template("job_item.html", now_active_tab=job.job_name,
                                  job_list=job_list, title=u"任务管理",
                                  job_conf=job.get_conf())

@job_blueprint.route('/view/create', methods=["GET", "POST"])
@_l.login_required
def job_create():
    """
    GET: 新建Job的页
    POST: 新建Job, 成功redirect到该job页面; 失败redirect到自己这页面"""
    if _f.request.method == "GET":
        return _f.render_template("job_create.html")
    elif _f.request.method == "POST":
        # create a new job
        conf = _f.request.form['conf']
        new_job = Job.create_job(_l.current_user, conf)
        if new_job is None:
            # 少配置
            pass
        else:
            # 新建subprocess, 并脱离主机进程跑, 该进程不能出错，如果该进程捕获到svd_tool出错,不管是exit status还是return false, 都自己将数据库的running status写(想要使用这里的User和Job的Model, 自己调用一次init_db?)，或者发邮件
            pass
