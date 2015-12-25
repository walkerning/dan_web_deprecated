# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os
import sys
import signal
import time
import subprocess
import traceback # for test

from dan import load_command_packages
from dan.common.utils import init_logging, setup_glog_environ

from dan_web.model.share import convert_shared_path
from dan_web.adapter.job_adapter import get_adapter
from dan_web.job_runner.conf import END_LOG_TOKEN
from dan_web.error import RunnerException
from dan_web.job_runner.runner import JobRunnerDaemon


def read_log_and_send(ws, log_file):

    now_message = open(log_file, 'r').read()
    # fixme: 这里可能会有些读不到, 最好给subprocess的tail设置多读几行,
    # 与now_message最后一个一样的句子之后的都要打印出来

    # Open subprocess in a long-time connection is fine.
    # Open the subprocess as soon as possible to avoid lose log.
    p = subprocess.Popen(['tail', '-n', '0', '-F', log_file], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    # must strip to get the last log
    now_message_list = now_message.strip('\n').split('\n')
    for message in now_message_list:
        ws.send(message)

    # logfile is changing,
    if now_message_list and now_message_list[-1].strip('\n') == END_LOG_TOKEN:
        p.terminate()
    else:
        for message in iter(p.stdout.readline, END_LOG_TOKEN):
            message = message.strip('\n')
            if message == END_LOG_TOKEN:
                break
            ws.send(message.strip('\n'))

    p.terminate()

def kill_running_job(job, trys=5):
    if job.job_status != 'running':
        return
    else:
        try:
            with open(job.pid_file, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            print("No pid file, something goes wrong!")
            raise
        #if pid != job.running_pid:
        # fixme: 以后应该不需要runing_pid这个项
        try_time = 0
        try:
            while try_time < trys:
                os.kill(pid, signal.SIGTERM)
                try_time += 1
                time.sleep(0.1) # 最多引入0.5s的延时, 记得先把其他按钮给禁掉
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(job.pid_file):
                    os.remove(job.pid_file)
            else:
                print(str(err))
                # fixme: just for test here
                raise


class JobRunner(object):
    """
    The Job Runner! Core function of this website!"""

    def __init__(self, job, db):
        self._job = job
        self._db = db
        self.job_adapter = get_adapter([('job_type', job.job_type)])()
        for cmd_type, cmd_cls in load_command_packages():
            if cmd_type == job.job_type:
                self.job_cls = cmd_cls
                break
        else:
            raise RunnerException('在当前环境的dan包里没有找到工具: %s'%job.job_type)

        # convert conf
        self.conf = self.job_adapter.convert_conf(job.get_conf(),
                                                  addition_converter={'input_file':
                                                                      [job.get_abs_data_file_path, convert_shared_path],
                                                                      'output_proto': job.get_abs_data_file_path,
                                                                      'output_caffemodel': job.get_abs_data_file_path

                                                                  })
        self.log_file = job.abs_log_file
        self.runner = self.job_cls.load_from_config(self.conf, hide_file_path=True)
        self.pid_file = job.pid_file

    def _set_end_status(self, runner):
        self._job.set_end_status(runner.end_status)

    def _init_logging_stderr(self, _):
        init_logging()
        # Make caffe log to stderr too!
        # And I don't think someone need caffe info logs
        # seem on the website
        setup_glog_environ(quiet=True, GLOG_logtostderr='1')

    def _init_pycaffe_path(self, _):
        # init pycaffe path for Python search path
        pycaffe_path = os.environ.get('DAN_WEB_PYCAFFE_PATH', None)
        if pycaffe_path is not None:
            sys.path.insert(0, pycaffe_path)

    def run(self):
        """
        fork新进程开始运行, return新进程的pid"""
        # log everything to stderr
        job_runner = JobRunnerDaemon(self.runner, self.pid_file,
                                     # stdout=self.log_file,
                                     stderr=self.log_file,
                                     #stderr=self.log_file,
                                     hooks={
                                         "at-exit": self._set_end_status,
                                         "pre-run": [self._init_logging_stderr,
                                                     self._init_pycaffe_path]

                                     })
        self._job.job_status = "running"
        try:
            center_pid = job_runner.start()
            _, status = os.waitpid(center_pid, 0) #fixme: 会不会出问题...
            if os.WIFEXITED(status):
                exit_status = os.WEXITSTATUS(status)
                if exit_status != 0:
                    self._job.job_status = "failed"
                    return False
            else:
                raise Exception('这不应该出现...debug!')

        except Exception as e:
            print("Exception when start or waitpid, ", e)
            try:
                exc_info = sys.exc_info()

            finally:
                # Display the *original* exception
                traceback.print_exception(*exc_info)
                del exc_info
                self._job.job_status = "failed"
                return False
        # fixme: also need another try, except
        self._db.session.add(self._job)
        self._db.session.commit()
        return True
