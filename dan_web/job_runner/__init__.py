# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os
import sys
import signal
import time
import subprocess
import yaml

# fixme: this website could easily be changed to not depend on dan, 
# but why would this website run without dan
# so, let it be.
# If in the future, we change the backend, maybe some modification is needed
from dan.common.utils import init_logging, setup_glog_environ

from dan_web.model.share import convert_shared_path
from dan_web.adapter.job_adapter import get_adapter
from dan_web.job_runner.conf import END_LOG_TOKEN
from dan_web.error import RunnerException, ExpectedException
from dan_web.job_runner.runner import JobRunnerDaemon
from dan_web.helper import which

def read_log_and_send(ws, log_file):
    now_message = open(log_file, 'r').read()
    now_message_list = now_message.strip('\n').split('\n')
    for message in now_message_list:
        if not message.strip('\n') == END_LOG_TOKEN:
            ws.send(message)
        else:
            break

def read_log_and_send_realtime(ws, log_file):

    now_message = open(log_file, 'r').read()
    # fixme: 这里可能会有些读不到, 最好给subprocess的tail设置多读几行,
    # 与now_message最后一个一样的句子之后的都要打印出来

    # Open subprocess in a long-time connection is fine.
    # Open the subprocess as soon as possible to avoid lose log.
    p = subprocess.Popen(['tail', '-n', '0', '-F', log_file], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, close_fds=True) # remember to close fds

    try:
        # must strip to get the last log
        now_message_list = now_message.strip('\n').split('\n')
        for message in now_message_list:
            if not message.strip('\n') == END_LOG_TOKEN:
                ws.send(message)
            else:
                p.terminate()
                return
    
        # logfile is changing,
        for message in iter(p.stdout.readline, END_LOG_TOKEN):
            message = message.strip('\n')
            if message == END_LOG_TOKEN:
                break
            ws.send(message.strip('\n'))
    
    except Exception:
        # 这里这样好不好...
        pass
    finally:
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
        try_time = 0
        try:
            while try_time < trys:
                os.kill(pid, signal.SIGTERM)
                try_time += 1
                time.sleep(0.1) # 最多引入0.5s的延时, 记得先把其他按钮给禁掉
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                #if os.path.exists(job.pid_file):
                #    os.remove(job.pid_file)
                pass
            else:
                print(str(err))
                # fixme: just for test here
                raise
        # fixme: 还是没有杀死怎么办
        if _is_pid_running(pid):
            print("没有杀死") # fortest
            raise ExpectedException('尝试了%d次, 不能杀死该进程' % trys)

def _is_pid_running(pid):
    return str(pid) in [_pid for _pid in os.listdir('/proc') if _pid.isdigit()]

class JobRunner(object):
    """
    The Job Runner! Core function of this website!"""
    TMP_CONF_DIR = '/tmp/dan_web/tmp_conf'
    def _get_tmp_conf_file(self, job):
        if not os.path.isdir(self.TMP_CONF_DIR):
            os.mkdir(self.TMP_CONF_DIR)
        return '/tmp/dan_web/tmp_conf/%d_%d.tmp.conf' % (job.user_id, job.job_id)

    def __init__(self, job, db):
        self._job = job
        self._db = db
        self.job_adapter = get_adapter([('job_type', job.job_type)])()
        if not which("dan"):
            raise RunnerException('在服务器环境的里没有找到dan')

        # convert conf
        self.conf = self.job_adapter.convert_conf(job.get_conf(),
                                                  addition_converter={'input_file':
                                                                      [job.get_abs_data_file_path, convert_shared_path],
                                                                      'output_proto': job.get_abs_data_file_path,
                                                                      'output_caffemodel': job.get_abs_data_file_path

                                                                  })
        self.conf['hide_file_path'] = True

        # dump temporary config file for danp
        self._tmp_conf_file = self.dump_dan_config_file()

        pycaffe_path =  os.environ.get('DAN_WEB_PYCAFFE_PATH', None)
        if pycaffe_path is not None:
            self.runner = ['dan', '-c', pycaffe_path, '-f', self._tmp_conf_file]
        else:
            self.runner = ['dan', '-f', self._tmp_conf_file]

        self.log_file = job.abs_log_file
        self.pid_file = job.pid_file

    def dump_dan_config_file(self):
        _tmp_conf_file = self._get_tmp_conf_file(self._job)
        tmp_dan_conf = {"pipeline" : [self._job.job_type], "config": {
            self._job.job_type: {
                "command" : self._job.job_type,
            }
        }}
        tmp_dan_conf["config"][self._job.job_type].update(self.conf)
        yaml.dump(tmp_dan_conf, open(_tmp_conf_file, 'w'))
        return _tmp_conf_file

    # def __init__(self, job, db):
    #     self._job = job
    #     self._db = db
    #     self.job_adapter = get_adapter([('job_type', job.job_type)])()
    #     for cmd_type, cmd_cls in load_command_packages():
    #         if cmd_type == job.job_type:
    #             self.job_cls = cmd_cls
    #             break
    #     else:
    #         raise RunnerException('在当前环境的dan包里没有找到工具: %s'%job.job_type)

    #     # convert conf
    #     self.conf = self.job_adapter.convert_conf(job.get_conf(),
    #                                               addition_converter={'input_file':
    #                                                                   [job.get_abs_data_file_path, convert_shared_path],
    #                                                                   'output_proto': job.get_abs_data_file_path,
    #                                                                   'output_caffemodel': job.get_abs_data_file_path

    #                                                               })
    #     self.log_file = job.abs_log_file
    #     self.runner = self.job_cls.load_from_config(self.conf, hide_file_path=True)
    #     self.pid_file = job.pid_file

    def _set_end_status(self, runner):
        self._job.set_end_status(runner.end_status)
        # try remove the temp config file
        try:
            os.remove(self._tmp_conf_file)
        except Exception:
            pass

    def _init_logging_stderr(self, _):
        init_logging()
        # Make caffe log to stderr too!
        # And I don't think someone need caffe info logs
        # seem on the website
        setup_glog_environ(quiet=True, GLOG_logtostderr='1') 
        # !glog only depend on environ(not sys.path),
        # so this should work for either cmd interface mode or the class runner mode

    def _init_pycaffe_path(self, _):
        """
        only for using the class runnner mode
        """
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
                                         "pre-run": [self._init_logging_stderr]#, 
                                                     #self._init_pycaffe_path] # only for class runner mode

                                     })
        self._job.job_status = "running"
        # must commit here, or there will be a race condition of this process and ...
        # the grand child process which do the _set_end_status callback
        self._db.session.commit() 
        try:
            center_pid = job_runner.start()
            _, status = os.waitpid(center_pid, 0) #fixme: 会不会出问题...
            if os.WIFEXITED(status):
                exit_status = os.WEXITSTATUS(status)
                if exit_status != 0:
                    self._job.job_status = "failed"
                    self._db.session.commit()
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
                self._db.session.commit()
                return False
        
        return True
