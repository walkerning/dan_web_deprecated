#-*- coding: utf-8 -*-
import os
import sys
from flask import Flask
app = Flask('hi')
here = os.path.dirname(os.path.abspath(__file__))
app.config.from_pyfile(os.path.join(here, 'app_conf.py'))
from dan_web.model import init_db
from flask.ext.sqlalchemy import SQLAlchemy
init_db(app)
from dan_web.model import (db, User, Job)
from dan_web.job_runner import JobRunner

# 在这里设置环境变量, 因为有时候也会作为独立脚本运行, 不使用subprocess.Popen指定env的方式
for env_name, env_value in app.config.get('WRITE_TO_ENV', {}).iteritems():
    os.environ[env_name] = env_value

# Default maximum for the number of available file descriptors.
# MAXFD = 1024

# import resource# Resource usage information.
# maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
# if (maxfd == resource.RLIM_INFINITY):
#     maxfd = MAXFD

# 实际使用的时候, subprocess.Popen做了这些事情
# Iterate through and close all file descriptors.
# 主要是不能打开着监听端口... 这也太傻逼了... 其他文件还好... 
# for fd in range(3, maxfd):
#     # 不能关闭标准输入输出对应的fd, 因为runner里要用到0,1,2三个file descriptor
#     try:
#         #os.close(fd)
#         os.fdopen(fd).close()
#     except OSError:# ERROR, fd wasn't open to begin with (ignored)
#         pass

try:
    job = Job.get(sys.argv[1])
    runner = JobRunner(job,db)
    status = runner.run()
    if status:
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    print e
    sys.exit(1)

