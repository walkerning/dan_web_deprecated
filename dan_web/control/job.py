# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import json

import flask as _f
from flask.ext import login as _l

from dan_web.helper import (success_json, fail_json, get_adapter)
from dan_web.model import (User, Job)
from dan_web.adapter.formview_adapter import FormViewAdapter
from dan_web.view_conf import ViewConfer

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
        # create a new job
        conf = _f.request.form['conf']
        new_job = Job.create_job(_l.current_user, conf)
        if new_job is None:
            # 少配置
            pass
        else:
            # 新建subprocess, 并脱离主机进程跑, 该进程不能出错，如果该进程捕获到svd_tool出错,不管是exit status还是return false, 都自己将数据库的running status写(想要使用这里的User和Job的Model, 自己调用一次init_db?)，或者发邮件
            pass


@job_blueprint.route('form/pre_ajax', methods=["POST"])
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
        return success_json(data=input_proto_list)
    elif name == 'input_caffemodel':
        # 找出所有的prototxt
        input_caffemodel_list = ['upload/' + x for x in _l.current_user.get_file_name_list('upload_caffemodel')]
        input_caffemodel_list += ['generated/' + x for x in _l.current_user.get_file_name_list('generated_caffemodel')]

        return success_json(data=input_caffemodel_list)
    else:
        # 以后如果要加更多还是放在adapter里, 其实还没有完全设计好...
        return fail_json()

@job_blueprint.route('form/post_ajax', methods=["POST"])
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