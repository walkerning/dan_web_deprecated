# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import subprocess
import json

import flask as _f
from flask.ext import login as _l

from dan_web.helper import success_json, fail_json
from dan_web.model import (User, Job, db)
from dan_web.model.share import get_shared_file_name_list
from dan_web.view_conf import ViewConfer

from dan_web.adapter.job_adapter import  get_adapter
from dan_web.adapter.secure import secure_conf
from dan_web.adapter.formview_adapter import FormViewAdapter

from dan_web.job_runner import JobRunner, kill_running_job

from dan_web.error import ExpectedException

here = os.path.dirname(os.path.abspath(__file__))
app_root = os.path.dirname(here)

job_blueprint = _f.Blueprint('job', __name__)

fv_adapter = FormViewAdapter(__name__, 'arg_templates')

view_confer = ViewConfer()

@job_blueprint.route('view/<job_id>', methods=["GET"])
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
        job_status = (job.job_status, view_confer.status_to_color(job.job_status))
        return _f.render_template("job_item.html", now_active_tab="jobid_" + str(job.job_id),
                                  job_id=str(job.job_id), title="任务管理",
                                  job_list=job_list, job_conf=job.get_conf(),
                                  job_name=job.job_name, job_type=view_confer.job_type_to_desc(job.job_type),
                                  job_status=job_status)

@job_blueprint.route('view/create', methods=["GET", "POST"])
@_l.login_required
def job_create():
    """
    GET: 新建Job的页
    POST: 新建Job, 成功redirect到该job页面; 失败redirect到自己这页面"""
    if _f.request.method == "GET":
        job_list = [(x.job_name, x.job_id) for x in Job.get_job_list_by_user_id(_l.current_user.user_id)]
        return _f.render_template("job_create.html", title="任务管理",
                                  now_active_tab="create-new-job",
                                  job_list=job_list)
    elif _f.request.method == "POST":
        # fixme: 其实可以改成ajax的..
        # create a new job
        # use get!!! or 400 will be returned by Flask!!!
        #conf = _f.request.form.get('conf', None)
        conf = {name: value for name, value in _f.request.form.iteritems()}
        # if conf is None:
        #     _f.flash('Job新建失败: 新建请求不能被识别', 'danger')
        #     return _f.redirect(_f.url_for('job.job_create'))

        # must secure user input a bit here
        job_type = conf.get('job_type', None)
        if not job_type:
            _f.flash('Job新建失败: 没有指定Job类型', 'danger')
            return _f.redirect(_f.url_for('job.job_create'))
        try:
            # fixme: 这个感觉在job里做更好, secure_conf里就可以不用重新update了
            conf = secure_conf(job_type, conf)
        except Exception:
            # fixme: 先raiseprint()
            raise
        try:
            new_job = Job.create_job(_l.current_user.user_id, conf)
        except ExpectedException as e:
            # 超过了job限制, 配置不完全(客户端也会检验)
            _f.flash('Job新建失败: %s' % e, 'danger')
            return _f.redirect(_f.url_for('job.job_create'))
        except Exception as e:
            # Internal Error, may be a bug, log to log file
            # fixme: add traceback here
            print(e)
            _f.flash('Job新建失败', 'danger')
            return _f.redirect(_f.url_for('job.job_create'))
        else:
            _f.flash('Job新建成功', 'success')
            return _f.redirect(_f.url_for('job.job_item', job_id=new_job.job_id))

@job_blueprint.route('ajax/job/run', methods=["POST"])
@_l.login_required
def job_run():
    job_id = _f.request.form.get('job')
    if job_id is None:
        return fail_json(error_string="运行Job失败: 没有提供job id")
    job = Job.get_job_of_user_id(job_id, _l.current_user.user_id)
    if job is None:
        return fail_json(error_string="运行Job失败: 不合法的Job运行请求")
    # 检查job状态
    if job.job_status == 'running':
        # fixme: 如果出现at-exit没有执行的情况怎么办...
        return fail_json(error_string="运行Job失败: 该Job已经在运行")
    # 新建子进程运行工具
    # try:
    #     job_runner = JobRunner(job, db)
    # except ExpectedException as e:
    #     # fixme: 有什么情况会导致新建成功但无法开始运行, 比如达到同时运行的job上限了?
    #     return fail_json(error_string='运行Job失败: ' + repr(e))
    # except Exception as e:
    #     print(e)
    #     return fail_json(error_string='运行Job失败')
    # fixme: 这个run也在里面raise? 应该不用吧
    runner = subprocess.Popen(['python', os.path.join(app_root, 'run_job.py'), str(job.job_id)])
    try:
        _, status = os.waitpid(runner.pid, 0)
        if os.WIFEXITED(status):
            exit_status = os.WEXITSTATUS(status)
            if exit_status != 0:
                return fail_json(error_string="运行Job失败")
    except Exception as e:
        print(e)
        raise
    # status = job_runner.run() # run() method will create a new subprocess and run it
    # a sub process forked from here will have context, and system.exit will be catch...
    # so cannot exit from the second process
    return success_json()

@job_blueprint.route('ajax/job/delete', methods=["POST"])
@_l.login_required
def job_delete():
    job_id = _f.request.form.get('job')
    if job_id is None:
        return fail_json(error_string="删除Job失败: 没有提供job id")
    job = Job.get_job_of_user_id(job_id, _l.current_user.user_id)
    if job is None:
        return fail_json(error_string="删除Job失败: 不合法的Job删除请求")
    # 检查job状态
    if job.job_status == 'running':
        return fail_json(error_string="删除Job失败: 该Job已经在运行, 请先中止")
    try:
        Job.delete_by_job_id(job_id)
    except Exception as e:
        print(e)
        return fail_json(error_string='删除Job失败')
    else:
        return success_json()

@job_blueprint.route('ajax/job/stop', methods=["POST"])
@_l.login_required
def job_stop():
    job_id = _f.request.form.get('job')
    if job_id is None:
        return fail_json(error_string="中止Job失败: 没有提供job id")
    job = Job.get_job_of_user_id(job_id, _l.current_user.user_id)
    if job is None:
        return fail_json(error_string="中止Job失败: 不合法的Job删除请求")
    # 检查Job status
    if not job.job_status == 'running':
        return fail_json(error_string="中止Job失败: 该Job没有在运行")
    try:
        kill_running_job(job)
    except Exception as e:
        print(e)
        return fail_json(error_string='中止Job失败: 尝试刷新或稍等')
    else:
        return success_json()

@job_blueprint.route('ajax/form/pre_ajax', methods=["POST"])
@_l.login_required
def pre_ajax():
    """
    实现所有表单里需要pre_ajax的逻辑.
    如果以后类型更多, 应该考虑把实际处理交给adapter, 每个工具的adapter去查看哪个配置选择的话需要新的哪个配置或者需要做什么, 现在逻辑感觉还不够清晰"""
    name = _f.request.form['name']
    if name == 'input_proto':
        # 找出所有的prototxt, 还可以给用户提供几个软链接到通用的VGG,.把下载/删除那个软链接的按钮给关掉, 并且下载的处理函数检查一下
        input_proto_list = ['upload/' + x for x in _l.current_user.get_file_name_list('upload_prototxt')]
        input_proto_list += ['generated/' + x for x in _l.current_user.get_file_name_list('generated_prototxt')]
        input_proto_list += ['shared/' + x for x in get_shared_file_name_list('*.prototxt')]
        return success_json(data=input_proto_list)
    elif name == 'input_caffemodel':
        # 找出所有的prototxt
        input_caffemodel_list = ['upload/' + x for x in _l.current_user.get_file_name_list('upload_caffemodel')]
        input_caffemodel_list += ['generated/' + x for x in _l.current_user.get_file_name_list('generated_caffemodel')]
        input_caffemodel_list += ['shared/' + x for x in get_shared_file_name_list('*.caffemodel')]
        return success_json(data=input_caffemodel_list)
    else:
        # 以后如果要加更多还是放在adapter里, 其实还没有完全设计好...
        return fail_json()

@job_blueprint.route('ajax/form/post_ajax', methods=["POST"])
@_l.login_required
def post_ajax():
    """
    实现所有表单里需要post_ajax的逻辑.
    如果以后类型更多, 应该考虑把实际处理交给adapter, 每个工具的adapter去查看哪个配置选择的话需要新的哪个配置"""
    json_str = _f.request.form.get('data', '')
    if not json_str:
        return fail_json(error_string='错误的参数')
    try:
        json_data = json.loads(json_str)
    except Exception:
        return fail_json(error_string='错误的json格式')
    name = json_data.get('name', '')
    value = json_data.get('value', '')
    create_by_list = json_data.get('create_by_list', [])
    if not name or not value:
        return fail_json(error_string='错误的参数')
    adapter_layers = []
    for create_by in reversed(create_by_list):
        create_by_name = create_by.get('name', '')
        create_by_value = create_by.get('value', '')
        if not create_by_name or not create_by_value:
            return fail_json(error_string='错误的Adapter')
        else:
            adapter_layers.append((create_by_name, create_by_value))
    adapter_layers.append((name, value))
    adapter = get_adapter(adapter_layers)

    if adapter is None:
        return fail_json(error_string='错误的Adapter')
    else:
        new_form_groups = fv_adapter.render_form(adapter.required, addition_info='create_by="%s"'%name, required=True)
        new_form_groups += fv_adapter.render_form(adapter.optional, addition_info='create_by="%s"'%name)
        return success_json(data=new_form_groups)
