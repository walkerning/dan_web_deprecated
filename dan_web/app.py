#-*- coding: utf-8 -*-
"""
Dan web
"""

from __future__ import unicode_literals, print_function
import os
import subprocess

import flask as _f
from flask.ext import login as _l
from werkzeug import secure_filename
from flask_sockets import Sockets

from dan_web.control import upload as _u
from dan_web.helper import success_json, fail_json
from dan_web.model import init_db

from dan_web.job_runner import read_log_and_send

here = os.path.dirname(os.path.abspath(__file__))

# init app
app = _f.Flask(__name__)
app.config.from_pyfile(os.path.join(here, 'app_conf.py'))

for env_name, env_value in app.config.get('WRITE_TO_ENV', {}).iteritems():
    os.environ[env_name] = env_value

app.debug = True #just for debug

# init database
init_db(app)
from dan_web.model import (User, Job)

# init login manager
# fixme: move to an independent module
login_manager = _l.LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'
login_manager.login_message = '请先登录'
login_manager.refresh_view = '请重新登录'

# here import job control !
from dan_web.control.job import job_blueprint
app.register_blueprint(job_blueprint, url_prefix="/job/")

# websocket, need wsgi middleware to correctly handle the websocket environ
sockets = Sockets(app) # patch app.wsgi_app for dispatching to ws handler with the app context

@sockets.route('/job/realtime_log')
@_l.login_required
def realtime_log(ws):
    """
    Get realtime logs by long-time websocket connection."""
    if ws.environ.get('wsgi.url_scheme', 'http') + '://' + ws.environ.get('HTTP_HOST', '127.0.0.1') != ws.origin:
        # 不同源拒绝连接
        return
    else:
        job_id = ws.receive()
        try:
            job = Job.get_job_of_user_id(int(job_id), _l.current_user.user_id)
            if job is None:
                return
        except:
            # job_id无效或者不是当前用户的job
            return
        else:
            if job.job_status == 'starting':
                ws.send("Error: 该Job还没有开始运行")
            elif job.log_deleted:
                ws.send("Error: 该Job运行的Log已经被删除")
            else:
                log_file = job.abs_log_file
                if not os.path.isfile(log_file):
                    # ???
                    ws.send("Error: 该Job还没有生成Log文件")
                elif job.job_status != 'running':
                    # logfile is not changing, just return the content
                    for message in iter(open(log_file, 'r').readline, ''):
                        ws.send(message)
                else:
                    read_log_and_send(ws, log_file)



@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# --- web hander ----
@app.route("/", methods=["GET"])
@_l.login_required
def index():
    """
    Dan website index page."""

    job_list = [(x.job_name, x.job_id) for x in Job.get_job_list_by_user_id(_l.current_user.user_id)]
    return _f.render_template('index_file.html', now_active_tab="file-manage",
                              job_list=job_list, title="文件管理")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if _f.request.method == 'GET':
        return _f.render_template('login.html')
    else:
        login_user = User.validate_and_get(_f.request.form['user_name'],
                                           _f.request.form['password'])
        if login_user is not None:
            _l.login_user(login_user)
            _f.flash('Logged in successfully.', 'success')
            return _f.redirect(_f.url_for('index'))
        else:
            _f.flash('Login error!', 'danger')
            return _f.redirect(_f.url_for('login'))

@app.route("/upload/", methods=["POST"])
@_l.login_required
def upload():
    #user = _l.current_user
    upload_file = _f.request.files['file']
    upload_file_type = _f.request.form.get('filetype', None)

    if not upload_file:
        return fail_json(error_string='没有上传文件')
    elif not upload_file_type:
        return fail_json(error_string='没有提供文件类型')
    elif not _u.allowed_filetype(upload_file_type):
        return fail_json(error_string=('不支持的文件类型: <%s>' % upload_file_type))
    elif not _u.allowed_file(upload_file_type, upload_file.filename):
        return fail_json(error_string=('不支持的文件名: "%s", '
                                       '应为 *.%s') % (
                                           upload_file.filename,
                                           upload_file_type))
    else:
        upload_filename = _u.get_upload_filename(_l.current_user.user_id,
                                              upload_file.filename,
                                              upload_file_type)
        upload_file.save(os.path.join(here, app.config['UPLOAD_DIR'], upload_filename))

        return success_json(filename=upload_filename)

@app.route("/refresh_file_list", methods=['POST'])
@_l.login_required
def refresh_file_list():
    # secure file name is very important
    dir_name = secure_filename(_f.request.form.get('dir_name', ''))
    if not dir_name:
        return fail_json(error_string='no dir_name specified')

    return success_json(file_list=_l.current_user.get_file_name_list(dir_name))

# 之后还是用nginx serve吧, 先这么写
@app.route("/download_file/<file_name>", methods=['GET'])
@_l.login_required
def download_file(file_name):
    file_name = secure_filename(file_name) # never trust user input
    dir_name = secure_filename(_f.request.args.get('dir_name', ''))

    if not dir_name or not file_name:
        return _f.abort(404)
    else:
        return _f.send_from_directory(_l.current_user.get_user_dir(dir_name),
                                      file_name)

@app.route("/delete_file", methods=['POST'])
@_l.login_required
def delete_file():
    dir_name = secure_filename(_f.request.form.get('dir_name', ''))
    file_name = secure_filename(_f.request.form.get('file_name', ''))
    # 可以进一步限制dir_name在那四个里面
    if not dir_name or not file_name:
        return fail_json(error_string='删除请求参数错误')
    else:
        try:
            _l.current_user.delete_user_file(dir_name, file_name)
        except Exception:
            return fail_json(error_string='删除文件失败')
        else:
            return success_json()


@app.route("/logout")
@_l.login_required
def logout():
    _l.logout_user()
    return _f.redirect(_f.url_for('login'))



if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "127.0.0.1"
    PORT = 8000
    app.debug = True
    app.run(port=PORT, host=host)
